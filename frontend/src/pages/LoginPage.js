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
    Grid,
    InputAdornment,
    IconButton
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import api from '../api/axios';

function LoginPage() {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });
    const [twoFactorCode, setTwoFactorCode] = useState('');
    const [is2FA, setIs2FA] = useState(false);
    const [userId, setUserId] = useState(null);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleClickShowPassword = () => setShowPassword((show) => !show);
    const handleMouseDownPassword = (event) => event.preventDefault();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await api.post('/security/login/', formData, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.data['2fa_required']) {
                setIs2FA(true);
                setUserId(response.data.user_id);
                setError('');
                return;
            }

            const { access } = response.data;
            if (access) {
                localStorage.setItem('token', access);
                navigate('/');
            } else {
                setError('Login failed. No access token received.');
            }

        } catch (err) {
            console.error(err);
            setError('Invalid username or password');
        }
    };

    const handle2FASubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await api.post('/security/login/2fa/', {
                user_id: userId,
                code: twoFactorCode
            });

            const { access } = response.data;
            if (access) {
                localStorage.setItem('token', access);
                navigate('/');
            }

        } catch (err) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.error) {
                setError(err.response.data.error);
            } else {
                setError('Invalid code');
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
                    <Typography component="h1" variant="h4" sx={{ mb: 3, fontWeight: 'bold', color: '#1976d2' }}>
                        {is2FA ? 'Verification' : 'Sign In'}
                    </Typography>

                    {error && (
                        <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    {!is2FA ? (
                        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                id="username"
                                label="Username"
                                name="username"
                                autoComplete="username"
                                autoFocus
                                value={formData.username}
                                onChange={handleChange}
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                name="password"
                                label="Password"
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                autoComplete="current-password"
                                value={formData.password}
                                onChange={handleChange}
                                InputProps={{
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <IconButton
                                                aria-label="toggle password visibility"
                                                onClick={handleClickShowPassword}
                                                onMouseDown={handleMouseDownPassword}
                                                edge="end"
                                            >
                                                {showPassword ? <VisibilityOff /> : <Visibility />}
                                            </IconButton>
                                        </InputAdornment>
                                    ),
                                }}
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                sx={{ mt: 3, mb: 2, py: 1.5, fontSize: '1rem' }}
                            >
                                Sign In
                            </Button>

                            <Grid container direction="column" spacing={1} alignItems="center">
                                <Grid item>
                                    <Link component={RouterLink} to="/password-reset" variant="body2">
                                        Forgot password?
                                    </Link>
                                </Grid>
                                <Grid item>
                                    <Link component={RouterLink} to="/register" variant="body2">
                                        {"Don't have an account? Sign Up"}
                                    </Link>
                                </Grid>
                            </Grid>

                            <Box sx={{ mt: 3, textAlign: 'center' }}>
                                <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                                    Can't remember your password? Try something fun!
                                </Typography>
                                <Button
                                    component={RouterLink}
                                    to="/difficult-login"
                                    variant="outlined"
                                    color="secondary"
                                    fullWidth
                                >
                                    Try Difficult Login Mode
                                </Button>
                            </Box>
                        </Box>
                    ) : (
                        <Box component="form" onSubmit={handle2FASubmit} sx={{ mt: 1, width: '100%' }}>
                            <Typography variant="body1" sx={{ mb: 2, textAlign: 'center' }}>
                                A verification code has been sent to your email.
                            </Typography>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                id="code"
                                label="Verification Code"
                                name="code"
                                autoFocus
                                value={twoFactorCode}
                                onChange={(e) => setTwoFactorCode(e.target.value)}
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                sx={{ mt: 3, mb: 2, py: 1.5, fontSize: '1rem' }}
                            >
                                Verify
                            </Button>
                            <Button
                                fullWidth
                                variant="text"
                                onClick={() => { setIs2FA(false); setTwoFactorCode(''); }}
                            >
                                Back to Login
                            </Button>
                        </Box>
                    )}
                </Paper>
            </Container>
        </Box>
    );
}

export default LoginPage;
