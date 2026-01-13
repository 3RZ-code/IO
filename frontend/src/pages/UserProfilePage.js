import { useState, useEffect } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  Grid,
  AppBar,
  Toolbar,
  Avatar,
  Divider,
  Card,
  CardContent,
  Chip,
  Stack,
  IconButton,
  InputAdornment,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
import CancelIcon from "@mui/icons-material/Cancel";
import PersonIcon from "@mui/icons-material/Person";
import EmailIcon from "@mui/icons-material/Email";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import SecurityIcon from "@mui/icons-material/Security";
import GroupIcon from "@mui/icons-material/Group";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import LockIcon from "@mui/icons-material/Lock";
import MailOutlineIcon from "@mui/icons-material/MailOutline";
import Switch from "@mui/material/Switch";
import FormControlLabel from "@mui/material/FormControlLabel";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import api from "../api/axios";

function UserProfilePage() {
  const [userData, setUserData] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    birth_date: "",
    username: "",
  });
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [changePasswordMode, setChangePasswordMode] = useState(false);
  const [resetPasswordDialog, setResetPasswordDialog] = useState(false);
  const [resetPasswordStep, setResetPasswordStep] = useState(1);
  const [resetPasswordData, setResetPasswordData] = useState({
    email: "",
    code: "",
    new_password: "",
    confirm_password: "",
  });
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [invitationCode, setInvitationCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await api.get("/security/users/me/");
      setUserData(response.data);
      setFormData({
        first_name: response.data.first_name || "",
        last_name: response.data.last_name || "",
        email: response.data.email || "",
        birth_date: response.data.birth_date || "",
        username: response.data.username || "",
      });
      setTwoFactorEnabled(response.data.two_factor_enabled || false);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to load user data");
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditToggle = () => {
    if (editMode) {
      setFormData({
        first_name: userData.first_name || "",
        last_name: userData.last_name || "",
        email: userData.email || "",
        birth_date: userData.birth_date || "",
        username: userData.username || "",
      });
    }
    setEditMode(!editMode);
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const response = await api.patch(
        `/security/users/${userData.id}/`,
        formData
      );
      setUserData(response.data);
      setEditMode(false);
      setSuccess("Profile updated successfully!");
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to update profile");
      }
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!passwordData.current_password) {
      setError("Current password is required");
      return;
    }

    if (!passwordData.new_password) {
      setError("New password is required");
      return;
    }

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError("New passwords don't match");
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (passwordData.new_password === passwordData.current_password) {
      setError("New password must be different from current password");
      return;
    }

    try {
      try {
        await api.post("/security/login/", {
          username: userData.username,
          password: passwordData.current_password,
        });
      } catch (loginErr) {
        setError("Current password is incorrect");
        return;
      }

      await api.patch(`/security/users/${userData.id}/`, {
        password: passwordData.new_password,
      });

      setSuccess("Password changed successfully!");
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      setChangePasswordMode(false);

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : err.response.data.password
            ? err.response.data.password.join(", ")
            : JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to change password. Please try again.");
      }
    }
  };

  const handleTwoFactorToggle = async (event) => {
    const newValue = event.target.checked;
    setError("");
    setSuccess("");

    try {
      await api.patch(`/security/users/${userData.id}/`, {
        two_factor_enabled: newValue,
      });

      setTwoFactorEnabled(newValue);
      setSuccess(
        newValue
          ? "Two-factor authentication enabled successfully!"
          : "Two-factor authentication disabled successfully!"
      );

      fetchUserData();

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to update two-factor authentication setting");
      }
    }
  };

  const handleResetPasswordRequest = async () => {
    setError("");
    setSuccess("");

    if (!resetPasswordData.email) {
      setError("Email is required");
      return;
    }

    try {
      await api.post("/security/password-reset/", {
        email: resetPasswordData.email,
      });

      setSuccess("Password reset code sent to your email!");
      setResetPasswordStep(2);

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to send reset code. Please try again.");
      }
    }
  };

  const handleResetPasswordConfirm = async () => {
    setError("");
    setSuccess("");

    if (!resetPasswordData.code) {
      setError("Code is required");
      return;
    }

    if (!resetPasswordData.new_password) {
      setError("New password is required");
      return;
    }

    if (resetPasswordData.new_password !== resetPasswordData.confirm_password) {
      setError("Passwords don't match");
      return;
    }

    if (resetPasswordData.new_password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    try {
      await api.post("/security/password-reset/confirm/", {
        email: resetPasswordData.email,
        code: resetPasswordData.code,
        new_password: resetPasswordData.new_password,
      });

      setSuccess("Password reset successfully!");
      setResetPasswordDialog(false);
      setResetPasswordStep(1);
      setResetPasswordData({
        email: "",
        code: "",
        new_password: "",
        confirm_password: "",
      });

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : err.response.data.error
            ? err.response.data.error
            : JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to reset password. Please try again.");
      }
    }
  };

  const handleResetPasswordChange = (e) => {
    const { name, value } = e.target;
    setResetPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleInvitationSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!invitationCode.trim()) {
      setError("Please enter an invitation code");
      return;
    }

    try {
      const response = await api.post("/security/group-invitations/accept/", {
        code: invitationCode.trim(),
      });

      setSuccess(`Successfully joined group '${response.data.group.name}'!`);
      setInvitationCode("");

      fetchUserData();

      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : err.response.data.error || JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to accept invitation. Please try again.");
      }
    }
  };

  const toggleShowPassword = (field) => {
    setShowPasswords((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case "admin":
        return "error";
      case "user":
        return "primary";
      case "spectator":
        return "default";
      default:
        return "default";
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#f5f5f5" }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            User Profile
          </Typography>
          <Button color="inherit" onClick={() => navigate("/")}>
            Home
          </Button>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ py: 4, pb: 10 }}>
        <Card elevation={3} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  bgcolor: "#1976d2",
                  fontSize: "2rem",
                  mr: 3,
                }}
              >
                {userData.username.charAt(0).toUpperCase()}
              </Avatar>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h4" gutterBottom>
                  {userData.first_name && userData.last_name
                    ? `${userData.first_name} ${userData.last_name}`
                    : userData.username}
                </Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Chip
                    label={userData.role.toUpperCase()}
                    color={getRoleBadgeColor(userData.role)}
                    size="small"
                  />
                  {userData.two_factor_enabled && (
                    <Chip
                      icon={<SecurityIcon />}
                      label="2FA Enabled"
                      color="success"
                      size="small"
                    />
                  )}
                </Stack>
              </Box>
              {!editMode && (
                <Button
                  variant="contained"
                  startIcon={<EditIcon />}
                  onClick={handleEditToggle}
                >
                  Edit Profile
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>

        <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ mb: 3, fontWeight: "bold", color: "#1976d2" }}
          >
            Profile Information
          </Typography>

          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  name="username"
                  value={formData.username}
                  disabled
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={!editMode}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  disabled={!editMode}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  disabled={!editMode}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Birth Date"
                  name="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={handleChange}
                  disabled={!editMode}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <CalendarTodayIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Role"
                  value={userData.role}
                  disabled
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SecurityIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
            </Grid>

            {editMode && (
              <Box sx={{ mt: 3, display: "flex", gap: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  startIcon={<SaveIcon />}
                >
                  Save Changes
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<CancelIcon />}
                  onClick={handleEditToggle}
                >
                  Cancel
                </Button>
              </Box>
            )}
          </form>
        </Paper>

        <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ mb: 2, fontWeight: "bold", color: "#1976d2" }}
          >
            <GroupIcon sx={{ mr: 1, verticalAlign: "middle" }} />
            My Groups
          </Typography>

          {userData.groups && userData.groups.length > 0 ? (
            <Stack
              direction="row"
              spacing={1}
              flexWrap="wrap"
              useFlexGap
              sx={{ mb: 3 }}
            >
              {userData.groups.map((group) => (
                <Chip
                  key={group.id}
                  label={group.name}
                  color="primary"
                  variant="outlined"
                  size="medium"
                />
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              You are not a member of any groups yet.
            </Typography>
          )}

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Join a Group
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter an invitation code to join a group
          </Typography>
          <form onSubmit={handleInvitationSubmit}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={8}>
                <TextField
                  fullWidth
                  label="Invitation Code"
                  placeholder="e.g. ABC12DEF"
                  value={invitationCode}
                  onChange={(e) =>
                    setInvitationCode(e.target.value.toUpperCase())
                  }
                  inputProps={{ maxLength: 8 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  sx={{ height: 56 }}
                >
                  Join Group
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>

        <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ mb: 2, fontWeight: "bold", color: "#1976d2" }}
          >
            Account Details
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Created At
              </Typography>
              <Typography variant="body1">
                {new Date(userData.created_at).toLocaleDateString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Last Updated
              </Typography>
              <Typography variant="body1">
                {new Date(userData.updated_at).toLocaleDateString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Terms Accepted
              </Typography>
              <Typography variant="body1">
                {userData.terms_accepted ? "✓ Yes" : "✗ No"}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Privacy Policy Accepted
              </Typography>
              <Typography variant="body1">
                {userData.privacy_policy_accepted ? "✓ Yes" : "✗ No"}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ mb: 3, fontWeight: "bold", color: "#1976d2" }}
          >
            <SecurityIcon sx={{ mr: 1, verticalAlign: "middle" }} />
            Security Settings
          </Typography>

          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Two-Factor Authentication (2FA)
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={twoFactorEnabled}
                    onChange={handleTwoFactorToggle}
                    color="primary"
                  />
                }
                label={twoFactorEnabled ? "2FA is enabled" : "2FA is disabled"}
              />
              <LockIcon
                color={twoFactorEnabled ? "primary" : "disabled"}
                sx={{ ml: 1 }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
              {twoFactorEnabled
                ? "You will receive a verification code via email when logging in."
                : "Enable two-factor authentication for enhanced account security."}
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Change Password
            </Typography>
            {!changePasswordMode ? (
              <Box>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Update your account password. You will need to enter your
                  current password.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<LockIcon />}
                  onClick={() => setChangePasswordMode(true)}
                >
                  Change Password
                </Button>
              </Box>
            ) : (
              <Box>
                <form onSubmit={handlePasswordSubmit}>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Current Password"
                        name="current_password"
                        type={showPasswords.current ? "text" : "password"}
                        value={passwordData.current_password}
                        onChange={handlePasswordChange}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => toggleShowPassword("current")}
                                edge="end"
                              >
                                {showPasswords.current ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="New Password"
                        name="new_password"
                        type={showPasswords.new ? "text" : "password"}
                        value={passwordData.new_password}
                        onChange={handlePasswordChange}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => toggleShowPassword("new")}
                                edge="end"
                              >
                                {showPasswords.new ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Confirm New Password"
                        name="confirm_password"
                        type={showPasswords.confirm ? "text" : "password"}
                        value={passwordData.confirm_password}
                        onChange={handlePasswordChange}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => toggleShowPassword("confirm")}
                                edge="end"
                              >
                                {showPasswords.confirm ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
                    <Button type="submit" variant="contained" color="primary">
                      Update Password
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setChangePasswordMode(false);
                        setPasswordData({
                          current_password: "",
                          new_password: "",
                          confirm_password: "",
                        });
                      }}
                    >
                      Cancel
                    </Button>
                  </Box>
                </form>
              </Box>
            )}
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Reset Password via Email
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Forgot your password? Receive a verification code via email to
              reset it.
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              startIcon={<MailOutlineIcon />}
              onClick={() => {
                setResetPasswordDialog(true);
                setResetPasswordData({
                  ...resetPasswordData,
                  email: userData.email,
                });
              }}
            >
              Send Reset Code to Email
            </Button>
          </Box>
        </Paper>
      </Container>

      <Dialog
        open={resetPasswordDialog}
        onClose={() => {
          setResetPasswordDialog(false);
          setResetPasswordStep(1);
          setResetPasswordData({
            email: "",
            code: "",
            new_password: "",
            confirm_password: "",
          });
          setError("");
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Reset Password - Step {resetPasswordStep} of 2
        </DialogTitle>
        <DialogContent>
          {resetPasswordStep === 1 ? (
            <Box sx={{ pt: 2 }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Enter your email address to receive a verification code.
              </Typography>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={resetPasswordData.email}
                onChange={handleResetPasswordChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          ) : (
            <Box sx={{ pt: 2 }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Enter the verification code sent to your email and your new
                password.
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Verification Code"
                    name="code"
                    value={resetPasswordData.code}
                    onChange={handleResetPasswordChange}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="New Password"
                    name="new_password"
                    type="password"
                    value={resetPasswordData.new_password}
                    onChange={handleResetPasswordChange}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Confirm New Password"
                    name="confirm_password"
                    type="password"
                    value={resetPasswordData.confirm_password}
                    onChange={handleResetPasswordChange}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setResetPasswordDialog(false);
              setResetPasswordStep(1);
              setResetPasswordData({
                email: "",
                code: "",
                new_password: "",
                confirm_password: "",
              });
              setError("");
            }}
          >
            Cancel
          </Button>
          {resetPasswordStep === 1 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleResetPasswordRequest}
            >
              Send Code
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={handleResetPasswordConfirm}
            >
              Reset Password
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {error && (
        <Box
          sx={{
            position: "fixed",
            bottom: 20,
            left: "50%",
            transform: "translateX(-50%)",
            width: "90%",
            maxWidth: "600px",
            zIndex: 9999,
          }}
        >
          <Alert severity="error" onClose={() => setError("")} elevation={6}>
            {error}
          </Alert>
        </Box>
      )}
      {success && (
        <Box
          sx={{
            position: "fixed",
            bottom: 20,
            left: "50%",
            transform: "translateX(-50%)",
            width: "90%",
            maxWidth: "600px",
            zIndex: 9999,
          }}
        >
          <Alert
            severity="success"
            onClose={() => setSuccess("")}
            elevation={6}
          >
            {success}
          </Alert>
        </Box>
      )}
    </Box>
  );
}

export default UserProfilePage;
