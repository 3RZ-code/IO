import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  Divider,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

function TermsOfServicePage() {
  const navigate = useNavigate();

  const handleClose = () => {
    window.close();
  };

  return (
    <Box sx={{ minHeight: "100vh", backgroundColor: "#f5f5f5", py: 4 }}>
      <Container maxWidth="md">
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleClose}
          sx={{ mb: 2 }}
        >
          Back
        </Button>

        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography
            variant="h3"
            gutterBottom
            sx={{ fontWeight: "bold", color: "#1976d2", mb: 3 }}
          >
            Terms of Service
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            Last Updated: January 9, 2026
          </Typography>

          <Divider sx={{ mb: 3 }} />

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            1. Acceptance of Terms
          </Typography>
          <Typography variant="body1" paragraph>
            By accessing and using the IO Project platform ("Service"), you
            agree to be bound by these Terms of Service ("Terms"). If you do not
            agree to these Terms, you may not access or use the Service. These
            Terms apply to all users, including administrators, regular users,
            and spectators.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            2. Description of Service
          </Typography>
          <Typography variant="body1" paragraph>
            IO Project is a user management and collaboration platform that
            provides:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                User registration and authentication services
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Two-factor authentication (2FA) for enhanced security
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Group management and collaboration features
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Role-based access control (Administrator, User, Spectator)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Password recovery and account management
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Email notifications and group invitations
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            3. User Accounts and Registration
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>3.1 Account Creation:</strong> To use the Service, you must
            create an account by providing accurate and complete information,
            including a valid email address, username, and password. You are
            responsible for maintaining the confidentiality of your account
            credentials.
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>3.2 Account Accuracy:</strong> You agree to provide
            accurate, current, and complete information during registration and
            to update such information to keep it accurate and complete.
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>3.3 Account Security:</strong> You are responsible for all
            activities that occur under your account. You must immediately
            notify us of any unauthorized use of your account or any other
            breach of security.
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>3.4 Age Requirement:</strong> You must be at least 13 years
            old to use this Service. By using the Service, you represent that
            you meet this age requirement.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            4. User Roles and Permissions
          </Typography>
          <Typography variant="body1" paragraph>
            The Service provides three types of user roles:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>Administrator:</strong> Full access to all features,
                including user management, group management, and system
                configuration.
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>User:</strong> Standard access to personal profile
                management, group participation, and collaboration features.
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Spectator:</strong> Limited read-only access to certain
                features.
              </Typography>
            </li>
          </Box>
          <Typography variant="body1" paragraph>
            Administrators reserve the right to modify user roles and
            permissions at any time.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            5. Groups and Invitations
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>5.1 Group Creation:</strong> Administrators can create
            groups and manage group memberships through the platform.
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>5.2 Group Invitations:</strong> Users may be invited to join
            groups via email invitation codes. Invitation codes are valid for 7
            days and are single-use only.
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>5.3 Group Participation:</strong> By joining a group, you
            agree to collaborate with other group members and follow any
            group-specific guidelines.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            6. Acceptable Use Policy
          </Typography>
          <Typography variant="body1" paragraph>
            You agree not to:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                Use the Service for any illegal purpose or in violation of any
                laws
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Attempt to gain unauthorized access to any part of the Service
                or other accounts
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Transmit any viruses, malware, or other harmful code
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Harass, abuse, or harm other users
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Share your account credentials with others
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Impersonate any person or entity
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Interfere with or disrupt the Service or servers
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            7. Two-Factor Authentication
          </Typography>
          <Typography variant="body1" paragraph>
            Users may enable two-factor authentication (2FA) for enhanced
            account security. When 2FA is enabled, you will receive a
            verification code via email during login. You are responsible for
            maintaining access to the email address associated with your
            account.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            8. Email Communications
          </Typography>
          <Typography variant="body1" paragraph>
            By using the Service, you consent to receive emails from us,
            including:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                Two-factor authentication codes
              </Typography>
            </li>
            <li>
              <Typography variant="body1">Password reset codes</Typography>
            </li>
            <li>
              <Typography variant="body1">Group invitation codes</Typography>
            </li>
            <li>
              <Typography variant="body1">
                Service updates and notifications
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            9. Intellectual Property
          </Typography>
          <Typography variant="body1" paragraph>
            The Service and its original content, features, and functionality
            are owned by IO Project and are protected by international
            copyright, trademark, patent, trade secret, and other intellectual
            property laws.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            10. Termination
          </Typography>
          <Typography variant="body1" paragraph>
            We reserve the right to suspend or terminate your account and access
            to the Service at our sole discretion, without notice, for conduct
            that we believe violates these Terms or is harmful to other users,
            us, or third parties, or for any other reason.
          </Typography>
          <Typography variant="body1" paragraph>
            You may terminate your account at any time by contacting an
            administrator or through your account settings.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            11. Disclaimer of Warranties
          </Typography>
          <Typography variant="body1" paragraph>
            THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT
            WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT
            LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
            PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            12. Limitation of Liability
          </Typography>
          <Typography variant="body1" paragraph>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, IO PROJECT SHALL NOT BE
            LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR
            PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER
            INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL,
            OR OTHER INTANGIBLE LOSSES.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            13. Changes to Terms
          </Typography>
          <Typography variant="body1" paragraph>
            We reserve the right to modify or replace these Terms at any time.
            If a revision is material, we will provide at least 30 days' notice
            prior to any new terms taking effect. Your continued use of the
            Service after such changes constitutes acceptance of the new Terms.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            14. Contact Information
          </Typography>
          <Typography variant="body1" paragraph>
            If you have any questions about these Terms, please contact us
            through the platform or by contacting your system administrator.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Box sx={{ textAlign: "center" }}>
            <Button
              variant="contained"
              onClick={handleClose}
              sx={{ minWidth: 200 }}
            >
              I Understand
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default TermsOfServicePage;
