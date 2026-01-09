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

function PrivacyPolicyPage() {
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
            Privacy Policy
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
            Introduction
          </Typography>
          <Typography variant="body1" paragraph>
            IO Project ("we", "our", or "us") is committed to protecting your
            privacy. This Privacy Policy explains how we collect, use, disclose,
            and safeguard your information when you use our platform. Please
            read this privacy policy carefully. If you do not agree with the
            terms of this privacy policy, please do not access the Service.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            1. Information We Collect
          </Typography>

          <Typography
            variant="h6"
            gutterBottom
            sx={{ mt: 2, fontWeight: "bold" }}
          >
            1.1 Personal Information
          </Typography>
          <Typography variant="body1" paragraph>
            We collect personal information that you voluntarily provide to us
            when you register on the platform, including:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">Username</Typography>
            </li>
            <li>
              <Typography variant="body1">Email address</Typography>
            </li>
            <li>
              <Typography variant="body1">
                Password (stored securely using encryption)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                First name and last name (optional)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">Date of birth (optional)</Typography>
            </li>
            <li>
              <Typography variant="body1">
                Google ID (if using Google authentication)
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h6"
            gutterBottom
            sx={{ mt: 2, fontWeight: "bold" }}
          >
            1.2 Account Activity Information
          </Typography>
          <Typography variant="body1" paragraph>
            We automatically collect certain information when you use the
            Service:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                Login history and authentication events
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Two-factor authentication status
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Group memberships and invitations
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Profile updates and modifications
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Account creation and update timestamps
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h6"
            gutterBottom
            sx={{ mt: 2, fontWeight: "bold" }}
          >
            1.3 Technical Information
          </Typography>
          <Typography variant="body1" paragraph>
            We may collect technical information including:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">IP address</Typography>
            </li>
            <li>
              <Typography variant="body1">Browser type and version</Typography>
            </li>
            <li>
              <Typography variant="body1">Device information</Typography>
            </li>
            <li>
              <Typography variant="body1">Operating system</Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            2. How We Use Your Information
          </Typography>
          <Typography variant="body1" paragraph>
            We use the information we collect for the following purposes:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>Account Management:</strong> To create and maintain your
                user account
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Authentication:</strong> To verify your identity and
                secure your account
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Two-Factor Authentication:</strong> To send verification
                codes via email for enhanced security
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Password Recovery:</strong> To send password reset codes
                when requested
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Group Management:</strong> To facilitate group
                invitations and memberships
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Communication:</strong> To send you important service
                updates and notifications
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Security:</strong> To detect and prevent fraud, abuse,
                and security incidents
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Service Improvement:</strong> To analyze usage patterns
                and improve the platform
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            3. Email Communications
          </Typography>
          <Typography variant="body1" paragraph>
            We send emails for the following purposes:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>Two-Factor Authentication:</strong> Verification codes
                sent during login (valid for 15 minutes)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Password Reset:</strong> Password reset codes (valid for
                15 minutes)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Group Invitations:</strong> Invitation codes to join
                groups (valid for 7 days)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Service Notifications:</strong> Important account and
                security updates
              </Typography>
            </li>
          </Box>
          <Typography variant="body1" paragraph>
            These emails are essential for the operation of your account and
            cannot be opted out of while you maintain an active account.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            4. How We Share Your Information
          </Typography>
          <Typography variant="body1" paragraph>
            We do not sell your personal information. We may share your
            information in the following circumstances:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>With Administrators:</strong> System administrators can
                view and manage user accounts, groups, and invitations
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>With Group Members:</strong> Your name and email may be
                visible to other members of groups you join
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>For Legal Reasons:</strong> When required by law or to
                protect our rights
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Service Providers:</strong> With third-party service
                providers who assist in operating our platform (e.g., email
                service providers)
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            5. Data Security
          </Typography>
          <Typography variant="body1" paragraph>
            We implement appropriate technical and organizational security
            measures to protect your personal information:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                Passwords are encrypted using industry-standard hashing
                algorithms
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Two-factor authentication is available for enhanced account
                security
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Verification codes expire after a short period (15 minutes for
                2FA and password reset)
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Access to user data is restricted to authorized administrators
                only
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                Secure HTTPS connections for all data transmission
              </Typography>
            </li>
          </Box>
          <Typography variant="body1" paragraph>
            However, no method of transmission over the Internet or electronic
            storage is 100% secure. While we strive to protect your personal
            information, we cannot guarantee absolute security.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            6. Data Retention
          </Typography>
          <Typography variant="body1" paragraph>
            We retain your personal information for as long as your account is
            active or as needed to provide you services. We will retain and use
            your information as necessary to comply with legal obligations,
            resolve disputes, and enforce our agreements.
          </Typography>
          <Typography variant="body1" paragraph>
            Verification codes (2FA, password reset) are automatically deleted
            after use or expiration. Group invitation codes are retained for 7
            days or until used.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            7. Your Rights and Choices
          </Typography>
          <Typography variant="body1" paragraph>
            You have the following rights regarding your personal information:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>Access:</strong> You can access and view your profile
                information at any time through your account settings
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Update:</strong> You can update your personal
                information (name, email, birth date) through your profile page
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Password:</strong> You can change your password at any
                time
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Two-Factor Authentication:</strong> You can enable or
                disable 2FA in your security settings
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Groups:</strong> You can view your group memberships and
                accept new invitations
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Account Deletion:</strong> You can request account
                deletion by contacting an administrator
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            8. Children's Privacy
          </Typography>
          <Typography variant="body1" paragraph>
            Our Service is not intended for children under the age of 13. We do
            not knowingly collect personal information from children under 13.
            If you are a parent or guardian and believe we have collected
            information from a child under 13, please contact us immediately.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            9. Role-Based Access
          </Typography>
          <Typography variant="body1" paragraph>
            Different user roles have different access levels to information:
          </Typography>
          <Box component="ul" sx={{ pl: 4, mb: 2 }}>
            <li>
              <Typography variant="body1">
                <strong>Administrators:</strong> Can view and manage all users,
                groups, and invitations
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Users:</strong> Can view and edit only their own profile
                and see their group memberships
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Spectators:</strong> Have limited read-only access
              </Typography>
            </li>
          </Box>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            10. Third-Party Services
          </Typography>
          <Typography variant="body1" paragraph>
            Our Service may contain links to third-party websites or integrate
            with third-party services (such as Google authentication). We are
            not responsible for the privacy practices of these third parties. We
            encourage you to read their privacy policies.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            11. International Data Transfers
          </Typography>
          <Typography variant="body1" paragraph>
            Your information may be transferred to and maintained on servers
            located outside of your state, province, country, or other
            governmental jurisdiction where data protection laws may differ. By
            using the Service, you consent to such transfers.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            12. Changes to This Privacy Policy
          </Typography>
          <Typography variant="body1" paragraph>
            We may update this Privacy Policy from time to time. We will notify
            you of any changes by posting the new Privacy Policy on this page
            and updating the "Last Updated" date. You are advised to review this
            Privacy Policy periodically for any changes.
          </Typography>

          <Typography
            variant="h5"
            gutterBottom
            sx={{ mt: 3, fontWeight: "bold" }}
          >
            13. Contact Us
          </Typography>
          <Typography variant="body1" paragraph>
            If you have questions or concerns about this Privacy Policy or our
            data practices, please contact us through the platform or reach out
            to your system administrator.
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

export default PrivacyPolicyPage;
