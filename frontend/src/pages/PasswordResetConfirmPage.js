import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    TextField,
    Button,
    Paper,
    Link,
    Alert,
    Grid
} from '@mui/material';
import api from '../api/axios';

function PasswordResetConfirmPage() {
    const location = useLocation();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        email: '',
        code: '',
        new_password: '',
        confirm_new_password: ''
    });
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        if (location.state && location.state.email) {
            setFormData(prev => ({ ...prev, email: location.state.email }));
        }
    }, [location.state]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        if (formData.new_password !== formData.confirm_new_password) {
            setError("Passwords don't match");
            return;
        }

        try {
            await api.post('/security/password-reset/confirm/', {
                email: formData.email,
                code: formData.code,
                new_password: formData.new_password
            });

            setMessage('Password has been reset successfully. Redirecting to login...');
            setTimeout(() => {
                navigate('/login');
            }, 2000);

        } catch (err) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.error) {
                setError(err.response.data.error);
            } else {
                setError('Failed to reset password. Please check your code and try again.');
            }
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f5f5f5',
            }}
        >
            <Container maxWidth="xs">
                <Paper
                    elevation={6}
                    sx={{
                        p: 4,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        borderRadius: 2,
                    }}
                >
                    <Typography component="h1" variant="h5" sx={{ mb: 3, fontWeight: 'bold', color: '#1976d2' }}>
                        Set New Password
                    </Typography>

                    {message && (
                        <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
                            {message}
                        </Alert>
                    )}

                    {error && (
                        <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email Address"
                            name="email"
                            autoComplete="email"
                            value={formData.email}
                            onChange={handleChange}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="code"
                            label="Reset Code"
                            name="code"
                            value={formData.code}
                            onChange={handleChange}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="new_password"
                            label="New Password"
                            type="password"
                            id="new_password"
                            value={formData.new_password}
                            onChange={handleChange}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="confirm_new_password"
                            label="Confirm New Password"
                            type="password"
                            id="confirm_new_password"
                            value={formData.confirm_new_password}
                            onChange={handleChange}
                        />

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, py: 1.5 }}
                        >
                            Reset Password
                        </Button>
                        <Grid container>
                            <Grid item xs>
                                <Link component={RouterLink} to="/login" variant="body2">
                                    Back to Login
                                </Link>
                            </Grid>
                        </Grid>
                    </Box>
                </Paper>
            </Container>
        </Box>
    );
}

export default PasswordResetConfirmPage;
