import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  Grid,
  AppBar,
  Toolbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Card,
  CardContent,
  Stack,
  Tooltip,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import SendIcon from "@mui/icons-material/Send";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import GroupAddIcon from "@mui/icons-material/GroupAdd";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import api from "../api/axios";

function AdminDashboardPage() {
  const [currentTab, setCurrentTab] = useState(0);
  const [users, setUsers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const [invitationDialog, setInvitationDialog] = useState(false);
  const [invitationForm, setInvitationForm] = useState({
    group_id: "",
    email: "",
  });
  const [generatedCode, setGeneratedCode] = useState("");
  const [createGroupDialog, setCreateGroupDialog] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [editUserDialog, setEditUserDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [editUserForm, setEditUserForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    role: "",
    group_ids: [],
  });

  useEffect(() => {
    fetchData();
  }, [currentTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, groupsRes, invitationsRes] = await Promise.all([
        api.get("/security/users/"),
        api.get("/security/groups/"),
        api.get("/security/group-invitations/"),
      ]);
      setUsers(usersRes.data);
      setGroups(groupsRes.data);
      setInvitations(invitationsRes.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to load data");
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const handleCreateGroup = async () => {
    setError("");
    setSuccess("");

    if (!newGroupName.trim()) {
      setError("Group name is required");
      return;
    }

    try {
      await api.post("/security/groups/", { name: newGroupName });
      setSuccess("Group created successfully!");
      setNewGroupName("");
      setCreateGroupDialog(false);
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      setError("Failed to create group");
    }
  };

  const handleDeleteGroup = async (groupId) => {
    if (!window.confirm("Are you sure you want to delete this group?")) {
      return;
    }

    try {
      await api.delete(`/security/groups/${groupId}/`);
      setSuccess("Group deleted successfully!");
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      setError("Failed to delete group");
    }
  };

  const handleCreateInvitation = async () => {
    setError("");
    setSuccess("");

    if (!invitationForm.group_id || !invitationForm.email) {
      setError("Please fill in all fields");
      return;
    }

    try {
      const response = await api.post(
        "/security/group-invitations/create/",
        invitationForm
      );
      setGeneratedCode(response.data.invitation.code);
      setSuccess(`Invitation created! Code: ${response.data.invitation.code}`);
      fetchData();
      setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMsg =
          typeof err.response.data === "string"
            ? err.response.data
            : err.response.data.error || JSON.stringify(err.response.data);
        setError(errorMsg);
      } else {
        setError("Failed to create invitation");
      }
    }
  };

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    setSuccess("Code copied to clipboard!");
    setTimeout(() => setSuccess(""), 2000);
  };

  const handleCloseInvitationDialog = () => {
    setInvitationDialog(false);
    setInvitationForm({ group_id: "", email: "" });
    setGeneratedCode("");
  };

  const handleDeleteInvitation = async (invitationId) => {
    try {
      await api.delete(`/security/group-invitations/${invitationId}/`);
      setSuccess("Invitation deleted successfully!");
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      setError("Failed to delete invitation");
    }
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setEditUserForm({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      email: user.email || "",
      role: user.role || "",
      group_ids: user.groups ? user.groups.map((g) => g.id) : [],
    });
    setEditUserDialog(true);
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user?")) {
      return;
    }

    try {
      await api.delete(`/security/users/${userId}/`);
      setSuccess("User deleted successfully!");
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error(err);
      setError("Failed to delete user");
    }
  };

  const handleUpdateUser = async () => {
    setError("");
    setSuccess("");

    try {
      await api.patch(`/security/users/${selectedUser.id}/`, editUserForm);
      setSuccess("User updated successfully!");
      setEditUserDialog(false);
      fetchData();
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
        setError("Failed to update user");
      }
    }
  };

  const handleCloseEditUserDialog = () => {
    setEditUserDialog(false);
    setSelectedUser(null);
    setEditUserForm({
      first_name: "",
      last_name: "",
      email: "",
      role: "",
      group_ids: [],
    });
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
            Admin Dashboard
          </Typography>
          <Button color="inherit" onClick={() => navigate("/")}>
            Home
          </Button>
          <Button color="inherit" onClick={() => navigate("/profile")}>
            Profile
          </Button>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4, pb: 10 }}>
        <Typography
          variant="h4"
          gutterBottom
          sx={{ mb: 3, fontWeight: "bold" }}
        >
          Administration Panel
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
          <Tabs
            value={currentTab}
            onChange={(e, newValue) => setCurrentTab(newValue)}
          >
            <Tab label="Users" />
            <Tab label="Groups" />
            <Tab label="Invitations" />
          </Tabs>
        </Box>

        {currentTab === 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography
              variant="h5"
              gutterBottom
              sx={{ mb: 3, color: "#1976d2" }}
            >
              User Management
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Username</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Email</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Name</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Role</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Groups</strong>
                    </TableCell>
                    <TableCell>
                      <strong>2FA</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Actions</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        {user.first_name || user.last_name
                          ? `${user.first_name} ${user.last_name}`
                          : "-"}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.role.toUpperCase()}
                          color={getRoleBadgeColor(user.role)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {user.groups && user.groups.length > 0 ? (
                          <Stack
                            direction="row"
                            spacing={0.5}
                            flexWrap="wrap"
                            useFlexGap
                          >
                            {user.groups.map((group) => (
                              <Chip
                                key={group.id}
                                label={group.name}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Stack>
                        ) : (
                          "-"
                        )}
                      </TableCell>
                      <TableCell>
                        {user.two_factor_enabled ? (
                          <CheckCircleIcon color="success" />
                        ) : (
                          <CancelIcon color="disabled" />
                        )}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleEditUser(user)}
                          sx={{ mr: 1 }}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          size="small"
                          onClick={() => handleDeleteUser(user.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}

        {currentTab === 1 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
              <Typography variant="h5" sx={{ color: "#1976d2" }}>
                Group Management
              </Typography>
              <Button
                variant="contained"
                startIcon={<GroupAddIcon />}
                onClick={() => setCreateGroupDialog(true)}
              >
                Create Group
              </Button>
            </Box>

            <Grid container spacing={3}>
              {groups.map((group) => (
                <Grid item xs={12} sm={6} md={4} key={group.id}>
                  <Card elevation={2}>
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Typography variant="h6" gutterBottom>
                          {group.name}
                        </Typography>
                        <IconButton
                          color="error"
                          size="small"
                          onClick={() => handleDeleteGroup(group.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Group ID: {group.id}
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<SendIcon />}
                        onClick={() => {
                          setInvitationForm({
                            ...invitationForm,
                            group_id: group.id,
                          });
                          setInvitationDialog(true);
                        }}
                        sx={{ mt: 2 }}
                        fullWidth
                      >
                        Send Invitation
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {currentTab === 2 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}
            >
              <Typography variant="h5" sx={{ color: "#1976d2" }}>
                Invitation Management
              </Typography>
              <Button
                variant="contained"
                startIcon={<PersonAddIcon />}
                onClick={() => setInvitationDialog(true)}
              >
                Create Invitation
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Code</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Group</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Email</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Created By</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Status</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Created</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Actions</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {invitations.map((invitation) => (
                    <TableRow key={invitation.id}>
                      <TableCell>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <Typography
                            sx={{
                              fontFamily: "monospace",
                              fontWeight: "bold",
                              bgcolor: "#f0f0f0",
                              px: 1,
                              py: 0.5,
                              borderRadius: 1,
                            }}
                          >
                            {invitation.code}
                          </Typography>
                          <Tooltip title="Copy code">
                            <IconButton
                              size="small"
                              onClick={() => handleCopyCode(invitation.code)}
                            >
                              <ContentCopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>{invitation.group_name}</TableCell>
                      <TableCell>{invitation.email}</TableCell>
                      <TableCell>{invitation.created_by_name}</TableCell>
                      <TableCell>
                        {invitation.used ? (
                          <Chip
                            label={`Used by ${invitation.used_by_name}`}
                            color="success"
                            size="small"
                          />
                        ) : (
                          <Chip label="Active" color="primary" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(invitation.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          color="error"
                          size="small"
                          onClick={() => handleDeleteInvitation(invitation.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Container>

      <Dialog
        open={createGroupDialog}
        onClose={() => setCreateGroupDialog(false)}
      >
        <DialogTitle>Create New Group</DialogTitle>
        <DialogContent sx={{ minWidth: 400, pt: 2 }}>
          <TextField
            fullWidth
            label="Group Name"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateGroupDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateGroup} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={invitationDialog} onClose={handleCloseInvitationDialog}>
        <DialogTitle>Create Group Invitation</DialogTitle>
        <DialogContent sx={{ minWidth: 400, pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Select Group</InputLabel>
                <Select
                  value={invitationForm.group_id}
                  label="Select Group"
                  onChange={(e) =>
                    setInvitationForm({
                      ...invitationForm,
                      group_id: e.target.value,
                    })
                  }
                >
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id}>
                      {group.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="User Email"
                type="email"
                value={invitationForm.email}
                onChange={(e) =>
                  setInvitationForm({
                    ...invitationForm,
                    email: e.target.value,
                  })
                }
              />
            </Grid>
            {generatedCode && (
              <Grid item xs={12}>
                <Alert severity="success">
                  <Typography variant="body2" gutterBottom>
                    Invitation code generated:
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mt: 1,
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        fontFamily: "monospace",
                        bgcolor: "#f0f0f0",
                        px: 2,
                        py: 1,
                        borderRadius: 1,
                      }}
                    >
                      {generatedCode}
                    </Typography>
                    <IconButton
                      color="primary"
                      onClick={() => handleCopyCode(generatedCode)}
                    >
                      <ContentCopyIcon />
                    </IconButton>
                  </Box>
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseInvitationDialog}>Close</Button>
          <Button
            onClick={handleCreateInvitation}
            variant="contained"
            disabled={!!generatedCode}
          >
            Generate Code
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={editUserDialog}
        onClose={handleCloseEditUserDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Edit User {selectedUser && `- ${selectedUser.username}`}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={editUserForm.first_name}
                onChange={(e) =>
                  setEditUserForm({
                    ...editUserForm,
                    first_name: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={editUserForm.last_name}
                onChange={(e) =>
                  setEditUserForm({
                    ...editUserForm,
                    last_name: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={editUserForm.email}
                onChange={(e) =>
                  setEditUserForm({ ...editUserForm, email: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={editUserForm.role}
                  label="Role"
                  onChange={(e) =>
                    setEditUserForm({ ...editUserForm, role: e.target.value })
                  }
                >
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="spectator">Spectator</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Groups</InputLabel>
                <Select
                  multiple
                  value={editUserForm.group_ids}
                  label="Groups"
                  onChange={(e) =>
                    setEditUserForm({
                      ...editUserForm,
                      group_ids: e.target.value,
                    })
                  }
                  renderValue={(selected) => (
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                      {selected.map((groupId) => {
                        const group = groups.find((g) => g.id === groupId);
                        return (
                          <Chip
                            key={groupId}
                            label={group?.name || groupId}
                            size="small"
                          />
                        );
                      })}
                    </Box>
                  )}
                >
                  {groups.map((group) => (
                    <MenuItem key={group.id} value={group.id}>
                      {group.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditUserDialog}>Cancel</Button>
          <Button onClick={handleUpdateUser} variant="contained">
            Save Changes
          </Button>
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

export default AdminDashboardPage;
