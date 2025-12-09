"""
AI Generator - generowanie opisów dla raportów i analiz
Korzysta z Groq API (opcjonalnie)
"""
import requests
import json
import re
from typing import Optional, Dict, Any
from ..config import GROQ_API_KEY, GROQ_MODEL


class AIGenerator:
    """Generator opisów z użyciem AI (Groq API)"""
    
    @staticmethod
    def is_available() -> bool:
        """Sprawdza czy AI jest dostępne (klucz API ustawiony)"""
        return GROQ_API_KEY is not None and GROQ_API_KEY != ''
    
    @staticmethod
    def generate_analysis_description(
        analysis_type: str,
        analysis_data: Dict[str, Any],
        readings_count: int
    ) -> Optional[str]:
        """
        Generuje opis analizy na podstawie danych
        
        Args:
            analysis_type: Typ analizy (TRENDS/PEAK/ANOMALY)
            analysis_data: Dane analizy (summary)
            readings_count: Liczba odczytów
        
        Returns:
            Wygenerowany opis lub None jeśli AI niedostępne
        """
        if not AIGenerator.is_available():
            return None
        
        try:
            # Generuj opis dla analysis_summary (2-3 zdania)
            if analysis_type == 'TRENDS':
                change = analysis_data.get('change_percentage', 0)
                trend = analysis_data.get('trend', 'stabilny')
                direction = analysis_data.get('trend_direction', 'brak')
                prompt = f"Opisz w 2-3 zdaniach po polsku trend zużycia energii: {trend}, kierunek {direction}, zmiana {change:.1f}% na podstawie {readings_count} pomiarów."

            elif analysis_type == 'PEAK':
                peak = analysis_data.get('peak_value', 0)
                count = analysis_data.get('peak_events_count', 0)
                avg = analysis_data.get('average_value', 0)
                prompt = f"Opisz w 2-3 zdaniach po polsku szczyt obciążenia: maksimum {peak:.1f} kW, średnia {avg:.1f} kW, {count} przekroczeń progu, na podstawie {readings_count} pomiarów."

            elif analysis_type == 'ANOMALY':
                count = analysis_data.get('anomaly_count', 0)
                stats = analysis_data.get('statistics', {})
                mean = stats.get('mean', 0) if stats else 0
                std = stats.get('std', 0) if stats else 0
                
                # Różne prompty w zależności czy są anomalie
                if count == 0:
                    # BRAK anomalii - pozytywny komunikat
                    prompt = f"""Analiza {readings_count} pomiarów energetycznych nie wykazała żadnych anomalii ani odchyleń.
                    
Kontekst: System energetyczny działa stabilnie bez nieprawidłowości.

Zadanie: Napisz krótkie podsumowanie (2-3 zdania) po polsku o stabilnej pracy systemu bez anomalii."""
                else:
                    # SĄ anomalie - szczegółowy opis
                    anomalies = analysis_data.get('anomalies', [])
                    prompt = f"""Wykryto {count} anomalii w {readings_count} pomiarach energetycznych.
                    
Statystyki:
- Średnia wartość: {mean:.2f} kW
- Odchylenie standardowe: {std:.2f} kW
- Liczba anomalii: {count}

Zadanie: Napisz krótkie podsumowanie (2-3 zdania) po polsku opisujące wykryte anomalie i ich znaczenie dla systemu."""

            else:
                return None
            
            # Wywołaj Groq API
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': GROQ_MODEL,
                    'messages': [
                        {'role': 'system', 'content': 'Jesteś ekspertem energetyki. Odpowiadaj zwięźle i konkretnie po polsku.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.6,
                    'max_tokens': 500
                },
                timeout=12
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                if not result:
                    print(f"✗ AI {analysis_type}: empty response from API")
                    return None
                
                # Walidacja - sprawdź czy odpowiedź zawiera polskie znaki i sensowne słowa
                # Odrzuć odpowiedzi ze zbyt dużą ilością nietypowych znaków
                polish_chars = sum(1 for c in result if c in 'aąbcćdeęfghijklłmnńoóprsśtuwyzźżAĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ ')
                total_chars = len(result)
                
                if total_chars > 0 and polish_chars / total_chars < 0.7:
                    print(f"✗ AI {analysis_type}: invalid response (too many non-polish chars: {polish_chars}/{total_chars})")
                    return None
                
                # Sprawdź czy nie ma zbyt dużo cyfr/symboli z rzędu
                if re.search(r'[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s.,!?:;\-()]{10,}', result):
                    print(f"✗ AI {analysis_type}: invalid response (suspicious character sequence)")
                    return None
                
                print(f"✓ AI {analysis_type}: {len(result)} chars - {result[:80]}...")
                return result
            else:
                resp_text = response.text[:200] if hasattr(response, 'text') else 'no text'
                print(f"✗ AI {analysis_type}: HTTP {response.status_code} - {resp_text}")
                return None
                
        except requests.Timeout:
            print(f"✗ AI {analysis_type}: timeout")
            return None
        except Exception as e:
            print(f"✗ AI {analysis_type}: {type(e).__name__}")
            return None
    
    @staticmethod
    def generate_report_description(
        criteria: Dict[str, Any],
        analyses_summaries: list,
        readings_count: int
    ) -> Optional[str]:
        """
        Generuje opis całego raportu
        
        Args:
            criteria: Kryteria raportu
            analyses_summaries: Lista podsumowań analiz
            readings_count: Liczba odczytów
        
        Returns:
            Wygenerowany opis lub None jeśli AI niedostępne
        """
        if not AIGenerator.is_available():
            return None
        
        try:
            # Executive summary prompt - bardziej konkretny
            period = f"{criteria.get('date_from', '?')} - {criteria.get('date_to', '?')}"
            
            prompt = f"""Raport energetyczny za okres {period}.

Dane:
- Liczba pomiarów: {readings_count}
- Lokalizacja: {criteria.get('location', 'N/A')}
- Typ urządzenia: {criteria.get('device_type', 'N/A')}

Zadanie: Napisz krótkie podsumowanie wykonawcze (3-4 zdania) po polsku. Opisz okres analizy i ogólny stan systemu energetycznego."""

            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': GROQ_MODEL,
                    'messages': [
                        {'role': 'system', 'content': 'Jesteś ekspertem energetycznym. Piszesz profesjonalne podsumowania raportów. Używaj tylko języka polskiego z polskimi znakami.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.5,
                    'max_tokens': 500
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                
                # Walidacja - sprawdź czy odpowiedź zawiera polskie znaki i sensowne słowa
                polish_chars = sum(1 for c in result if c in 'aąbcćdeęfghijklłmnńoóprsśtuwyzźżAĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ ')
                total_chars = len(result)
                
                if total_chars > 0 and polish_chars / total_chars < 0.7:
                    print(f"✗ AI Report: invalid response (too many non-polish chars: {polish_chars}/{total_chars})")
                    return None
                
                # Sprawdź czy nie ma zbyt dużo cyfr/symboli z rzędu
                if re.search(r'[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s.,!?:;\-()]{10,}', result):
                    print(f"✗ AI Report: invalid response (suspicious character sequence)")
                    return None
                
                print(f"✓ AI Report: {len(result)} chars")
                return result
            else:
                print(f"✗ AI Report: HTTP {response.status_code}")
                return None
                
        except requests.Timeout:
            print(f"✗ AI Report: timeout")
            return None
        except Exception as e:
            print(f"✗ AI Report: {type(e).__name__}")
            return None
