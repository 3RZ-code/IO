import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  IconButton,
  TextField,
  Modal,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import api from "../api/axios";

const GAME_WIDTH = 350;
const GAME_HEIGHT = 400;
const PADDLE_WIDTH = 60;
const PADDLE_HEIGHT = 10;
const LETTER_SIZE = 20;

function DifficultLoginPage() {
  const canvasRef = useRef(null);
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [activeField, setActiveField] = useState("username");
  const [error, setError] = useState("");
  const [gameState, setGameState] = useState("playing");
  const [is2FA, setIs2FA] = useState(false);
  const [twoFactorCode, setTwoFactorCode] = useState("");
  const [userId, setUserId] = useState(null);

  const navigate = useNavigate();

  const paddleX = useRef(GAME_WIDTH / 2 - PADDLE_WIDTH / 2);
  const letters = useRef([]);
  const requestRef = useRef();
  const lastSpawnTime = useRef(0);
  const keysPressed = useRef({});

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        keysPressed.current[e.key] = true;
      }
    };
    const handleKeyUp = (e) => {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        keysPressed.current[e.key] = false;
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, []);

  const activeFieldRef = useRef(activeField);
  useEffect(() => {
    activeFieldRef.current = activeField;
  }, [activeField]);

  useEffect(() => {
    const update = (time) => {
      if (gameState !== "playing") {
        return;
      }

      if (time - lastSpawnTime.current > 600) {
        const chars =
          "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        const char = chars[Math.floor(Math.random() * chars.length)];
        letters.current.push({
          char,
          x: Math.random() * (GAME_WIDTH - LETTER_SIZE),
          y: 0,
          speed: Math.random() * 0.5 + 0.5,
        });
        lastSpawnTime.current = time;
      }

      if (keysPressed.current["ArrowLeft"]) {
        paddleX.current = Math.max(0, paddleX.current - 3);
      }
      if (keysPressed.current["ArrowRight"]) {
        paddleX.current = Math.min(
          GAME_WIDTH - PADDLE_WIDTH,
          paddleX.current + 3
        );
      }

      const ctx = canvasRef.current.getContext("2d");
      ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

      ctx.strokeStyle = "#e0e0e0";
      ctx.strokeRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

      ctx.fillStyle = "#1976d2";
      ctx.shadowBlur = 4;
      ctx.shadowColor = "#1976d2";
      ctx.fillRect(
        paddleX.current,
        GAME_HEIGHT - PADDLE_HEIGHT - 10,
        PADDLE_WIDTH,
        PADDLE_HEIGHT
      );
      ctx.shadowBlur = 0;

      for (let i = letters.current.length - 1; i >= 0; i--) {
        const l = letters.current[i];
        l.y += l.speed;

        ctx.fillStyle = "#333";
        ctx.font = "bold 20px Roboto";
        ctx.fillText(l.char, l.x, l.y);

        const paddleY = GAME_HEIGHT - PADDLE_HEIGHT - 10;
        if (
          l.y >= paddleY &&
          l.y < paddleY + PADDLE_HEIGHT + 5 &&
          l.x + 10 >= paddleX.current &&
          l.x <= paddleX.current + PADDLE_WIDTH
        ) {
          const currentField = activeFieldRef.current;
          setFormData((prev) => ({
            ...prev,
            [currentField]: prev[currentField] + l.char,
          }));
          letters.current.splice(i, 1);
        } else if (l.y > GAME_HEIGHT) {
          letters.current.splice(i, 1);
        }
      }

      requestRef.current = requestAnimationFrame(update);
    };
    requestRef.current = requestAnimationFrame(update);
    return () => cancelAnimationFrame(requestRef.current);
  }, [gameState]);

  const handleLogin = async () => {
    setGameState("submitting");
    setError("");
    try {
      const response = await api.post("/security/login/", formData, {
        headers: { "Content-Type": "application/json" },
      });

      if (response.data["2fa_required"]) {
        setGameState("2fa");
        setIs2FA(true);
        setUserId(response.data.user_id);
        setError("");
        return;
      }

      const { access } = response.data;
      if (access) {
        localStorage.setItem("token", access);
        navigate("/");
      } else {
        setError("Login failed.");
        setGameState("playing");
      }
    } catch (err) {
      console.error(err);
      setError("Invalid credentials.");
      setGameState("playing");
    }
  };

  const handle2FASubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await api.post("/security/login/2fa/", {
        user_id: userId,
        code: twoFactorCode,
      });

      const { access } = response.data;
      if (access) {
        localStorage.setItem("token", access);
        navigate("/");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Invalid code");
      }
    }
  };

  const handleClear = () => {
    setFormData((prev) => ({ ...prev, [activeField]: "" }));
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f5f5f5",
      }}
    >
      <Container maxWidth="xs">
        <Paper
          elevation={6}
          sx={{
            p: 4,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            borderRadius: 2,
            position: "relative",
          }}
        >
          <IconButton
            onClick={() => navigate("/login")}
            sx={{ position: "absolute", top: 8, left: 8 }}
          >
            <ArrowBackIcon />
          </IconButton>

          <Typography
            component="h1"
            variant="h4"
            sx={{ mb: 3, fontWeight: "bold", color: "#1976d2" }}
          >
            Sign In (Hard)
          </Typography>

          <Typography
            variant="body2"
            sx={{ mb: 2, textAlign: "center", color: "text.secondary" }}
          >
            Catch falling letters to type! Use Arrow Keys.
          </Typography>

          {error && !is2FA && (
            <Typography color="error" align="center" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          <Box
            sx={{
              width: "100%",
              opacity: is2FA ? 0.3 : 1,
              pointerEvents: is2FA ? "none" : "auto",
            }}
          >
            <TextField
              margin="normal"
              fullWidth
              label="Username"
              value={formData.username}
              InputProps={{
                readOnly: true,
              }}
              focused={activeField === "username"}
              onClick={() => setActiveField("username")}
              sx={{
                cursor: "pointer",
                "& .MuiInputBase-input": { cursor: "pointer" },
              }}
            />
            <TextField
              margin="normal"
              fullWidth
              label="Password"
              type="password"
              value={formData.password}
              InputProps={{
                readOnly: true,
              }}
              focused={activeField === "password"}
              onClick={() => setActiveField("password")}
              sx={{
                cursor: "pointer",
                "& .MuiInputBase-input": { cursor: "pointer" },
              }}
            />

            <Box
              sx={{
                mt: 2,
                mb: 2,
                display: "flex",
                justifyContent: "center",
                border: "1px solid #ddd",
                borderRadius: 1,
                overflow: "hidden",
              }}
            >
              <canvas
                ref={canvasRef}
                width={GAME_WIDTH}
                height={GAME_HEIGHT}
                style={{ display: "block" }}
              />
            </Box>

            <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
              <Button
                fullWidth
                variant="outlined"
                color="warning"
                onClick={handleClear}
              >
                Clear Field
              </Button>
            </Box>

            <Button
              fullWidth
              variant="contained"
              onClick={handleLogin}
              sx={{ mt: 1, mb: 2, py: 1.5, fontSize: "1rem" }}
            >
              Sign In
            </Button>
          </Box>

          <Modal
            open={is2FA}
            onClose={() => {
              setIs2FA(false);
              setGameState("playing");
            }}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Paper
              sx={{
                p: 4,
                width: 300,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
                Two-Factor Verification
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, textAlign: "center" }}>
                Enter the code sent to your email.
              </Typography>

              {error && (
                <Typography color="error" sx={{ mb: 1, fontSize: "0.875rem" }}>
                  {error}
                </Typography>
              )}

              <Box
                component="form"
                onSubmit={handle2FASubmit}
                sx={{ width: "100%" }}
              >
                <TextField
                  fullWidth
                  label="Code"
                  value={twoFactorCode}
                  onChange={(e) => setTwoFactorCode(e.target.value)}
                  autoFocus
                  sx={{ mb: 2 }}
                />
                <Button type="submit" fullWidth variant="contained">
                  Verify
                </Button>
                <Button
                  fullWidth
                  sx={{ mt: 1 }}
                  onClick={() => {
                    setIs2FA(false);
                    setGameState("playing");
                  }}
                >
                  Cancel
                </Button>
              </Box>
            </Paper>
          </Modal>
        </Paper>
      </Container>
    </Box>
  );
}

export default DifficultLoginPage;
