import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
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

function PasswordResetRequestPage() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            await api.post('/security/password-reset/', { email });
            setMessage('If an account exists with this email, a reset code has been sent.');
            setTimeout(() => {
                navigate('/password-reset/confirm', { state: { email } });
            }, 2000);

        } catch (err) {
            console.error(err);
            setError('Failed to send reset request. Please try again.');
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
                        Reset Password
                    </Typography>

                    <Typography variant="body2" sx={{ mb: 2, textAlign: 'center' }}>
                        Enter your email address and we will send you a code to reset your password.
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
                            autoFocus
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, py: 1.5 }}
                        >
                            Send Reset Code
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

export default PasswordResetRequestPage;
