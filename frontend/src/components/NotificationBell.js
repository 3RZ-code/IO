import { useState, useEffect } from 'react';
import {
    IconButton,
    Badge,
    Menu,
    MenuItem,
    Typography,
    Box,
    Divider,
    Button
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    Circle as CircleIcon
} from '@mui/icons-material';
import {
    getNotifications,
    getUnreadNotificationsCount,
    markNotificationAsRead,
    markAllNotificationsAsRead
} from '../api/alarmAlertService';

function NotificationBell() {
    const [anchorEl, setAnchorEl] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        fetchUnreadCount();
        // Opcjonalnie: odświeżaj co 30 sekund
        const interval = setInterval(fetchUnreadCount, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchUnreadCount = async () => {
        try {
            const data = await getUnreadNotificationsCount();
            setUnreadCount(data.unread_count);
        } catch (err) {
            console.error('Error fetching unread count:', err);
        }
    };

    const fetchNotifications = async () => {
        try {
            const data = await getNotifications();
            setNotifications(data.slice(0, 10)); // Pokaż tylko 10 najnowszych
        } catch (err) {
            console.error('Error fetching notifications:', err);
        }
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
        fetchNotifications();
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleMarkAsRead = async (notificationId) => {
        try {
            await markNotificationAsRead(notificationId);
            fetchNotifications();
            fetchUnreadCount();
        } catch (err) {
            console.error('Error marking as read:', err);
        }
    };

    const handleMarkAllAsRead = async () => {
        try {
            await markAllNotificationsAsRead();
            fetchNotifications();
            fetchUnreadCount();
        } catch (err) {
            console.error('Error marking all as read:', err);
        }
    };

    return (
        <>
            <IconButton color="inherit" onClick={handleClick}>
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsIcon />
                </Badge>
            </IconButton>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                PaperProps={{
                    sx: { width: 360, maxHeight: 480 }
                }}
            >
                <Box sx={{ px: 2, py: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Powiadomienia</Typography>
                    {unreadCount > 0 && (
                        <Button size="small" onClick={handleMarkAllAsRead}>
                            Oznacz wszystkie
                        </Button>
                    )}
                </Box>
                <Divider />

                {notifications.length === 0 ? (
                    <MenuItem disabled>
                        <Typography variant="body2" color="textSecondary">
                            Brak powiadomień
                        </Typography>
                    </MenuItem>
                ) : (
                    notifications.map((notification) => (
                        <MenuItem
                            key={notification.notification_id}
                            onClick={() => !notification.is_read && handleMarkAsRead(notification.notification_id)}
                            sx={{
                                bgcolor: notification.is_read ? 'inherit' : 'action.hover',
                                '&:hover': { bgcolor: 'action.selected' }
                            }}
                        >
                            <Box sx={{ width: '100%' }}>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                    {!notification.is_read && (
                                        <CircleIcon sx={{ fontSize: 8, color: 'primary.main', mt: 1 }} />
                                    )}
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                        <Typography
                                            variant="body2"
                                            sx={{
                                                fontWeight: notification.is_read ? 400 : 600,
                                                whiteSpace: 'normal',
                                                wordBreak: 'break-word'
                                            }}
                                        >
                                            {notification.message}
                                        </Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            {new Date(notification.sent_at).toLocaleString('pl-PL')}
                                        </Typography>
                                    </Box>
                                </Box>
                            </Box>
                        </MenuItem>
                    ))
                )}

                {notifications.length > 0 && (
                    <>
                        <Divider />
                        <Box sx={{ p: 1, textAlign: 'center' }}>
                            <Button size="small" fullWidth onClick={handleClose}>
                                Zobacz wszystkie
                            </Button>
                        </Box>
                    </>
                )}
            </Menu>
        </>
    );
}

export default NotificationBell;
