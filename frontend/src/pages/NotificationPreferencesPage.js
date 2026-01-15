import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Paper,
    Switch,
    FormControlLabel,
    TextField,
    Button,
    Alert,
    Divider,
    AppBar,
    Toolbar
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { getMyPreferences, updateMyPreferences } from '../api/alarmAlertService';

function NotificationPreferencesPage() {
    const navigate = useNavigate();
    const [preferences, setPreferences] = useState({
        is_active: true,
        quiet_hours_start: '',
        quiet_hours_end: ''
    });
    const [loading, setLoading] = useState(true);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchPreferences();
    }, []);

    const fetchPreferences = async () => {
        try {
            setLoading(true);
            const data = await getMyPreferences();
            setPreferences({
                is_active: data.is_active,
                quiet_hours_start: data.quiet_hours_start || '',
                quiet_hours_end: data.quiet_hours_end || ''
            });
        } catch (err) {
            console.error('Error fetching preferences:', err);
            setError('Nie udało się pobrać preferencji');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            await updateMyPreferences(preferences);
            setSuccess('Preferencje zapisane pomyślnie');
            setError('');
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            console.error('Error saving preferences:', err);
            setError('Nie udało się zapisać preferencji');
            setSuccess('');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Ustawienia Powiadomień
                    </Typography>
                    <Button color="inherit" onClick={() => navigate('/')}>
                        Home
                    </Button>
                    <Button color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>

            <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Zarządzanie Powiadomieniami
                </Typography>

            {success && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
                    {success}
                </Alert>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Ogólne
                </Typography>
                <FormControlLabel
                    control={
                        <Switch
                            checked={preferences.is_active}
                            onChange={(e) => setPreferences({ ...preferences, is_active: e.target.checked })}
                        />
                    }
                    label="Włącz powiadomienia"
                />
                <Typography variant="body2" color="textSecondary" sx={{ ml: 4, mb: 3 }}>
                    Wyłączenie spowoduje brak otrzymywania jakichkolwiek powiadomień
                </Typography>

                <Divider sx={{ my: 3 }} />

                <Typography variant="h6" gutterBottom>
                    Godziny Ciszy (Quiet Hours)
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    W wybranych godzinach nie będziesz otrzymywać powiadomień
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                    <TextField
                        label="Od"
                        type="time"
                        value={preferences.quiet_hours_start}
                        onChange={(e) => setPreferences({ ...preferences, quiet_hours_start: e.target.value })}
                        InputLabelProps={{ shrink: true }}
                        inputProps={{ step: 300 }}
                        fullWidth
                    />
                    <TextField
                        label="Do"
                        type="time"
                        value={preferences.quiet_hours_end}
                        onChange={(e) => setPreferences({ ...preferences, quiet_hours_end: e.target.value })}
                        InputLabelProps={{ shrink: true }}
                        inputProps={{ step: 300 }}
                        fullWidth
                    />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSave}
                        disabled={loading}
                    >
                        Zapisz
                    </Button>
                </Box>
            </Paper>

            <Paper sx={{ p: 3, mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Informacje
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                    • Powiadomienia są wysyłane automatycznie przy tworzeniu nowych alertów
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                    • Otrzymasz powiadomienie gdy ktoś potwierdzi Twój alert
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    • Administratorzy otrzymują wszystkie powiadomienia o potwierdzeniach
                </Typography>
            </Paper>
        </Container>
    </Box>
    );
}

export default NotificationPreferencesPage;
