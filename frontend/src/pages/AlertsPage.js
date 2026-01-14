import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Button,
    IconButton,
    TextField,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    Grid,
    Card,
    CardContent,
    AppBar,
    Toolbar
} from '@mui/material';
import {
    CheckCircle as CheckIcon,
    VolumeOff as MuteIcon,
    Refresh as RefreshIcon,
    Add as AddIcon,
    Delete as DeleteIcon
} from '@mui/icons-material';
import {
    getAlerts,
    getAlertStatistics,
    confirmAlert,
    muteAlert,
    createAlert,
    deleteAlert
} from '../api/alarmAlertService';

function AlertsPage() {
    const navigate = useNavigate();
    const [alerts, setAlerts] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState({
        severity: '',
        status: '',
        category: ''
    });
    const [openCreateDialog, setOpenCreateDialog] = useState(false);
    const [newAlert, setNewAlert] = useState({
        title: '',
        description: '',
        severity: 'INFO',
        category: '',
        source: ''
    });

    const fetchAlerts = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getAlerts(filters);
            setAlerts(data);
            setError('');
        } catch (err) {
            console.error('Error fetching alerts:', err);
            setError('Nie udało się pobrać alertów');
        } finally {
            setLoading(false);
        }
    }, [filters]);

    const fetchStatistics = useCallback(async () => {
        try {
            const stats = await getAlertStatistics();
            setStatistics(stats);
        } catch (err) {
            console.error('Error fetching statistics:', err);
        }
    }, []);

    useEffect(() => {
        fetchAlerts();
        fetchStatistics();
    }, [fetchAlerts, fetchStatistics]);

    const handleConfirm = async (alertId) => {
        try {
            await confirmAlert(alertId);
            fetchAlerts();
            fetchStatistics();
        } catch (err) {
            setError('Nie udało się potwierdzić alertu');
        }
    };

    const handleMute = async (alertId) => {
        try {
            await muteAlert(alertId);
            fetchAlerts();
            fetchStatistics();
        } catch (err) {
            setError('Nie udało się wyciszyć alertu');
        }
    };

    const handleDelete = async (alertId) => {
        if (window.confirm('Czy na pewno chcesz usunąć ten alert?')) {
            try {
                await deleteAlert(alertId);
                fetchAlerts();
                fetchStatistics();
            } catch (err) {
                setError('Nie udało się usunąć alertu');
            }
        }
    };

    const handleCreateAlert = async () => {
        try {
            await createAlert(newAlert);
            setOpenCreateDialog(false);
            setNewAlert({
                title: '',
                description: '',
                severity: 'INFO',
                category: '',
                source: ''
            });
            fetchAlerts();
            fetchStatistics();
        } catch (err) {
            setError('Nie udało się utworzyć alertu');
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'CRITICAL': return 'error';
            case 'WARNING': return 'warning';
            case 'INFO': return 'info';
            default: return 'default';
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'NEW': return 'primary';
            case 'CONFIRMED': return 'success';
            case 'MUTED': return 'default';
            case 'CLOSED': return 'secondary';
            default: return 'default';
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
                        Alerty i Powiadomienia
                    </Typography>
                    <Button color="inherit" onClick={() => navigate('/')}>
                        Home
                    </Button>
                    <Button color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h4" component="h1">
                        Zarządzanie Alertami
                    </Typography>
                    <Box>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => setOpenCreateDialog(true)}
                            sx={{ mr: 1 }}
                        >
                            Nowy Alert
                        </Button>
                        <IconButton onClick={() => { fetchAlerts(); fetchStatistics(); }}>
                            <RefreshIcon />
                        </IconButton>
                    </Box>
                </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                    {error}
                </Alert>
            )}

            {/* Statystyki */}
            {statistics && (
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Łącznie
                                </Typography>
                                <Typography variant="h4">
                                    {statistics.total}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ borderLeft: 3, borderColor: 'error.main' }}>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Krytyczne
                                </Typography>
                                <Typography variant="h4" color="error">
                                    {statistics.by_severity.CRITICAL}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ borderLeft: 3, borderColor: 'warning.main' }}>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Ostrzeżenia
                                </Typography>
                                <Typography variant="h4" color="warning.main">
                                    {statistics.by_severity.WARNING}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ borderLeft: 3, borderColor: 'primary.main' }}>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Nowe
                                </Typography>
                                <Typography variant="h4" color="primary">
                                    {statistics.by_status.NEW}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Filtry */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                        <FormControl fullWidth>
                            <InputLabel id="severity-label" shrink>Poziom Krytyczności</InputLabel>
                            <Select
                                labelId="severity-label"
                                value={filters.severity}
                                label="Poziom Krytyczności"
                                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                                displayEmpty
                                notched
                            >
                                <MenuItem value="">Wszystkie</MenuItem>
                                <MenuItem value="CRITICAL">Krytyczne</MenuItem>
                                <MenuItem value="WARNING">Ostrzeżenie</MenuItem>
                                <MenuItem value="INFO">Informacyjne</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <FormControl fullWidth>
                            <InputLabel id="status-label" shrink>Status</InputLabel>
                            <Select
                                labelId="status-label"
                                value={filters.status}
                                label="Status"
                                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                                displayEmpty
                                notched
                            >
                                <MenuItem value="">Wszystkie</MenuItem>
                                <MenuItem value="NEW">Nowe</MenuItem>
                                <MenuItem value="CONFIRMED">Potwierdzone</MenuItem>
                                <MenuItem value="MUTED">Wyciszone</MenuItem>
                                <MenuItem value="CLOSED">Zamknięte</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <TextField
                            fullWidth
                            label="Kategoria"
                            value={filters.category}
                            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                        />
                    </Grid>
                </Grid>
            </Paper>

            {/* Tabela alertów */}
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Tytuł</TableCell>
                            <TableCell>Opis</TableCell>
                            <TableCell>Krytyczność</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Kategoria</TableCell>
                            <TableCell>Źródło</TableCell>
                            <TableCell>Data</TableCell>
                            <TableCell align="right">Akcje</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={8} align="center">
                                    Ładowanie...
                                </TableCell>
                            </TableRow>
                        ) : alerts.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={8} align="center">
                                    Brak alertów
                                </TableCell>
                            </TableRow>
                        ) : (
                            alerts.map((alert) => (
                                <TableRow key={alert.alert_id}>
                                    <TableCell>{alert.title}</TableCell>
                                    <TableCell>{alert.description}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={alert.severity}
                                            color={getSeverityColor(alert.severity)}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            label={alert.status}
                                            color={getStatusColor(alert.status)}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>{alert.category}</TableCell>
                                    <TableCell>{alert.source}</TableCell>
                                    <TableCell>
                                        {new Date(alert.created_at).toLocaleString('pl-PL')}
                                    </TableCell>
                                    <TableCell align="right">
                                        {alert.status === 'NEW' && (
                                            <>
                                                <IconButton
                                                    color="success"
                                                    onClick={() => handleConfirm(alert.alert_id)}
                                                    title="Potwierdź"
                                                >
                                                    <CheckIcon />
                                                </IconButton>
                                                <IconButton
                                                    color="default"
                                                    onClick={() => handleMute(alert.alert_id)}
                                                    title="Wycisz"
                                                >
                                                    <MuteIcon />
                                                </IconButton>
                                            </>
                                        )}
                                        <IconButton
                                            color="error"
                                            onClick={() => handleDelete(alert.alert_id)}
                                            title="Usuń"
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Dialog tworzenia alertu */}
            <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Utwórz Nowy Alert</DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <TextField
                            fullWidth
                            label="Tytuł"
                            value={newAlert.title}
                            onChange={(e) => setNewAlert({ ...newAlert, title: e.target.value })}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            fullWidth
                            label="Opis"
                            multiline
                            rows={3}
                            value={newAlert.description}
                            onChange={(e) => setNewAlert({ ...newAlert, description: e.target.value })}
                            sx={{ mb: 2 }}
                        />
                        <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Poziom Krytyczności</InputLabel>
                            <Select
                                value={newAlert.severity}
                                label="Poziom Krytyczności"
                                onChange={(e) => setNewAlert({ ...newAlert, severity: e.target.value })}
                            >
                                <MenuItem value="INFO">Informacyjne</MenuItem>
                                <MenuItem value="WARNING">Ostrzeżenie</MenuItem>
                                <MenuItem value="CRITICAL">Krytyczne</MenuItem>
                            </Select>
                        </FormControl>
                        <TextField
                            fullWidth
                            label="Kategoria"
                            value={newAlert.category}
                            onChange={(e) => setNewAlert({ ...newAlert, category: e.target.value })}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            fullWidth
                            label="Źródło"
                            value={newAlert.source}
                            onChange={(e) => setNewAlert({ ...newAlert, source: e.target.value })}
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenCreateDialog(false)}>Anuluj</Button>
                    <Button onClick={handleCreateAlert} variant="contained" color="primary">
                        Utwórz
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    </Box>
    );
}

export default AlertsPage;
