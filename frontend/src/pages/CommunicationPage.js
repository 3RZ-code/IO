import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Alert,
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
  Stack,
  Tooltip,
  Grid,
  Card,
  CardContent,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import HomeIcon from "@mui/icons-material/Home";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import ForumIcon from "@mui/icons-material/Forum";
import api from "../api/axios";

function CommunicationPage() {
  const [schedules, setSchedules] = useState([]);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Dialog states
  const [createDialog, setCreateDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  
  // Form state
  const [scheduleForm, setScheduleForm] = useState({
    device: "",
    start_date: "",
    finish_date: "",
    working_period: "",
    working_status: false,
  });

  useEffect(() => {
    fetchData();
    checkAdmin();
  }, []);

  const checkAdmin = async () => {
    try {
      const response = await api.get("/security/users/me/");
      setIsAdmin(response.data.role === "admin");
      setCurrentUser(response.data);
    } catch (err) {
      console.error("Failed to check admin status:", err);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [schedulesRes, devicesRes] = await Promise.all([
        api.get("/communication/schedules/"),
        api.get("/data-acquisition/devices/"),
      ]);
      setSchedules(schedulesRes.data);
      setDevices(devicesRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to load schedules and devices");
      setLoading(false);
    }
  };

  const handleCreateSchedule = async () => {
    setError("");
    setSuccess("");

    // Validation
    if (
      !scheduleForm.device ||
      !scheduleForm.start_date ||
      !scheduleForm.finish_date ||
      !scheduleForm.working_period
    ) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      const payload = {
        ...scheduleForm,
        user_id: currentUser?.user_id?.toString() || "1",
      };
      
      await api.post("/communication/schedules/", payload);
      setSuccess("Schedule created successfully!");
      setCreateDialog(false);
      resetForm();
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error("Error creating schedule:", err);
      const errorMsg =
        err.response?.data?.finish_date?.[0] ||
        err.response?.data?.detail ||
        "Failed to create schedule";
      setError(errorMsg);
    }
  };

  const handleUpdateSchedule = async () => {
    setError("");
    setSuccess("");

    if (!selectedSchedule) return;

    try {
      const payload = {
        ...scheduleForm,
        user_id: currentUser?.user_id?.toString() || "1",
      };
      
      await api.put(
        `/communication/schedules/${selectedSchedule.schedule_id}/`,
        payload
      );
      setSuccess("Schedule updated successfully!");
      setEditDialog(false);
      setSelectedSchedule(null);
      resetForm();
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error("Error updating schedule:", err);
      const errorMsg =
        err.response?.data?.finish_date?.[0] ||
        err.response?.data?.detail ||
        "Failed to update schedule";
      setError(errorMsg);
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!window.confirm("Are you sure you want to delete this schedule?")) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await api.delete(`/communication/schedules/${scheduleId}/`);
      setSuccess("Schedule deleted successfully!");
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error("Error deleting schedule:", err);
      setError("Failed to delete schedule");
    }
  };

  const handleToggleStatus = async (schedule) => {
    setError("");
    setSuccess("");

    try {
      await api.patch(
        `/communication/schedules/${schedule.schedule_id}/update_status/`,
        {
          working_status: !schedule.working_status,
        }
      );
      setSuccess(
        `Schedule ${!schedule.working_status ? "activated" : "deactivated"}!`
      );
      fetchData();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      console.error("Error toggling status:", err);
      const errorMsg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        err.response?.data?.message ||
        (err.response?.status === 403 ? "You don't have permission to perform this action. Admin role required." : "Failed to update schedule status");
      setError(errorMsg);
    }
  };

  const openCreateDialog = () => {
    resetForm();
    setCreateDialog(true);
  };

  const openEditDialog = (schedule) => {
    setSelectedSchedule(schedule);
    setScheduleForm({
      device: schedule.device,
      start_date: schedule.start_date,
      finish_date: schedule.finish_date,
      working_period: schedule.working_period,
      working_status: schedule.working_status,
    });
    setEditDialog(true);
  };

  const resetForm = () => {
    setScheduleForm({
      device: "",
      start_date: "",
      finish_date: "",
      working_period: "",
      working_status: false,
    });
  };

  const handleCloseDialogs = () => {
    setCreateDialog(false);
    setEditDialog(false);
    setSelectedSchedule(null);
    resetForm();
    setError("");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const getDeviceName = (deviceId) => {
    const device = devices.find((d) => d.device_id === deviceId);
    return device ? device.name : `Device ${deviceId}`;
  };

  const getDeviceType = (deviceId) => {
    const device = devices.find((d) => d.device_id === deviceId);
    return device ? device.device_type : "Unknown";
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <ForumIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Communication Module - Schedule Management
          </Typography>
          <IconButton color="inherit" onClick={() => navigate("/")} sx={{ mr: 1 }}>
            <HomeIcon />
          </IconButton>
          {isAdmin && (
            <IconButton
              color="inherit"
              onClick={() => navigate("/admin")}
              sx={{ mr: 1 }}
            >
              <AdminPanelSettingsIcon />
            </IconButton>
          )}
          <IconButton
            color="inherit"
            onClick={() => navigate("/profile")}
            sx={{ mr: 2 }}
          >
            <AccountCircleIcon />
          </IconButton>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Stack spacing={3}>
            {/* Header */}
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Typography variant="h4" component="h1">
                Device Schedules
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={openCreateDialog}
                disabled={!isAdmin}
              >
                Create Schedule
              </Button>
            </Box>

            {/* Alerts */}
            {error && (
              <Alert severity="error" onClose={() => setError("")}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" onClose={() => setSuccess("")}>
                {success}
              </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Schedules
                    </Typography>
                    <Typography variant="h4">{schedules.length}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Active Schedules
                    </Typography>
                    <Typography variant="h4">
                      {schedules.filter((s) => s.working_status).length}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Inactive Schedules
                    </Typography>
                    <Typography variant="h4">
                      {schedules.filter((s) => !s.working_status).length}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>
                      Total Devices
                    </Typography>
                    <Typography variant="h4">{devices.length}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Schedules Table */}
            {loading ? (
              <Typography>Loading schedules...</Typography>
            ) : schedules.length === 0 ? (
              <Typography align="center" color="text.secondary" sx={{ py: 4 }}>
                No schedules found. Create your first schedule to get started.
              </Typography>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Device</TableCell>
                      <TableCell>Device Type</TableCell>
                      <TableCell>Start Date</TableCell>
                      <TableCell>Finish Date</TableCell>
                      <TableCell>Working Period</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {schedules.map((schedule) => (
                      <TableRow key={schedule.schedule_id}>
                        <TableCell>{schedule.schedule_id}</TableCell>
                        <TableCell>
                          {schedule.device_name || getDeviceName(schedule.device)}
                        </TableCell>
                        <TableCell>
                          {schedule.device_type || getDeviceType(schedule.device)}
                        </TableCell>
                        <TableCell>{schedule.start_date}</TableCell>
                        <TableCell>{schedule.finish_date}</TableCell>
                        <TableCell>{schedule.working_period}</TableCell>
                        <TableCell>
                          <Chip
                            label={
                              schedule.working_status ? "Active" : "Inactive"
                            }
                            color={schedule.working_status ? "success" : "default"}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip
                            title={
                              schedule.working_status
                                ? "Deactivate"
                                : "Activate"
                            }
                          >
                            <IconButton
                              color={
                                schedule.working_status ? "error" : "success"
                              }
                              onClick={() => handleToggleStatus(schedule)}
                              disabled={!isAdmin}
                            >
                              {schedule.working_status ? (
                                <StopIcon />
                              ) : (
                                <PlayArrowIcon />
                              )}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton
                              color="primary"
                              onClick={() => openEditDialog(schedule)}
                              disabled={!isAdmin}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              color="error"
                              onClick={() =>
                                handleDeleteSchedule(schedule.schedule_id)
                              }
                              disabled={!isAdmin}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Stack>
        </Paper>
      </Container>

      {/* Create Schedule Dialog */}
      <Dialog
        open={createDialog}
        onClose={handleCloseDialogs}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Schedule</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <FormControl fullWidth required>
              <InputLabel>Device</InputLabel>
              <Select
                value={scheduleForm.device}
                label="Device"
                onChange={(e) =>
                  setScheduleForm({ ...scheduleForm, device: e.target.value })
                }
              >
                {devices.map((device) => (
                  <MenuItem key={device.device_id} value={device.device_id}>
                    {device.name} ({device.device_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Start Date"
              type="date"
              fullWidth
              required
              value={scheduleForm.start_date}
              onChange={(e) =>
                setScheduleForm({ ...scheduleForm, start_date: e.target.value })
              }
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Finish Date"
              type="date"
              fullWidth
              required
              value={scheduleForm.finish_date}
              onChange={(e) =>
                setScheduleForm({
                  ...scheduleForm,
                  finish_date: e.target.value,
                })
              }
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Working Period"
              type="time"
              fullWidth
              required
              value={scheduleForm.working_period}
              onChange={(e) =>
                setScheduleForm({
                  ...scheduleForm,
                  working_period: e.target.value,
                })
              }
              InputLabelProps={{ shrink: true }}
              helperText="Format: HH:MM:SS"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleCreateSchedule}
            variant="contained"
            color="primary"
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Schedule Dialog */}
      <Dialog
        open={editDialog}
        onClose={handleCloseDialogs}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Schedule</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 2 }}>
            <FormControl fullWidth required>
              <InputLabel>Device</InputLabel>
              <Select
                value={scheduleForm.device}
                label="Device"
                onChange={(e) =>
                  setScheduleForm({ ...scheduleForm, device: e.target.value })
                }
              >
                {devices.map((device) => (
                  <MenuItem key={device.device_id} value={device.device_id}>
                    {device.name} ({device.device_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Start Date"
              type="date"
              fullWidth
              required
              value={scheduleForm.start_date}
              onChange={(e) =>
                setScheduleForm({ ...scheduleForm, start_date: e.target.value })
              }
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Finish Date"
              type="date"
              fullWidth
              required
              value={scheduleForm.finish_date}
              onChange={(e) =>
                setScheduleForm({
                  ...scheduleForm,
                  finish_date: e.target.value,
                })
              }
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Working Period"
              type="time"
              fullWidth
              required
              value={scheduleForm.working_period}
              onChange={(e) =>
                setScheduleForm({
                  ...scheduleForm,
                  working_period: e.target.value,
                })
              }
              InputLabelProps={{ shrink: true }}
              helperText="Format: HH:MM:SS"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button
            onClick={handleUpdateSchedule}
            variant="contained"
            color="primary"
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default CommunicationPage;
