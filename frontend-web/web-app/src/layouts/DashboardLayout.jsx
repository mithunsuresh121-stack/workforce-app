import React, { useState } from "react";
import {
  Box,
  Stack,
  Typography,
  Avatar,
  Button,
  IconButton,
  Collapse,
  TextField,
  InputAdornment,
  Tooltip,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  ChartBarIcon,
  UsersIcon,
  FolderIcon,
  Bars3Icon,
  BellIcon,
  ClockIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  DocumentIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import { useNavigate } from "react-router-dom";

export default function DashboardLayout({ children }) {
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [sidebarCollapsed, setSidebarCollapsed] = useState(isMobile);

  return (
    <Stack direction="column" sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      {/* Topbar */}
      <Box
        component="header"
        sx={{
          height: 64,
          px: 3,
          borderBottom: 1,
          borderColor: "divider",
          bgcolor: "background.paper",
          display: "grid",
          gridTemplateColumns: "auto 1fr auto",
          alignItems: "center",
          gap: 2,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
            <Bars3Icon style={{ width: 24, height: 24 }} />
          </IconButton>
          <Typography variant="h5" sx={{ color: 'text.primary' }}>Workforce Dashboard</Typography>
        </Box>
        <TextField
          placeholder="Search..."
          size="small"
          sx={{ maxWidth: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <MagnifyingGlassIcon style={{ width: 20, height: 20 }} />
              </InputAdornment>
            ),
          }}
        />
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton>
            <BellIcon style={{ width: 24, height: 24 }} />
          </IconButton>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>SA</Avatar>
        </Box>
      </Box>

      <Stack direction="row" flex={1}>
        {/* Sidebar */}
        <Collapse in={!sidebarCollapsed} orientation="horizontal">
          <Box
            component="aside"
            sx={{
              width: 240,
              borderRight: 1,
              borderColor: "divider",
              py: 3,
              px: 2,
              bgcolor: "background.paper",
            }}
          >
            <Stack direction="column" spacing={1}>
              <Tooltip title="Dashboard Overview" placement="right">
                <Button
                  variant="text"
                  startIcon={<ChartBarIcon />}
                  onClick={() => navigate("/dashboard")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Overview
                </Button>
              </Tooltip>
              <Tooltip title="Manage Employees" placement="right">
                <Button
                  variant="text"
                  startIcon={<UsersIcon />}
                  onClick={() => navigate("/employees")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Employees
                </Button>
              </Tooltip>
              <Tooltip title="Project Management" placement="right">
                <Button
                  variant="text"
                  startIcon={<FolderIcon />}
                  onClick={() => navigate("/projects")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Projects
                </Button>
              </Tooltip>
              <Tooltip title="Task Management" placement="right">
                <Button
                  variant="text"
                  startIcon={<CheckCircleIcon />}
                  onClick={() => navigate("/tasks")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Tasks
                </Button>
              </Tooltip>
              <Tooltip title="Attendance Tracking" placement="right">
                <Button
                  variant="text"
                  startIcon={<ClockIcon />}
                  onClick={() => navigate("/attendance")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Attendance
                </Button>
              </Tooltip>
              <Tooltip title="Leave Requests" placement="right">
                <Button
                  variant="text"
                  startIcon={<CalendarDaysIcon />}
                  onClick={() => navigate("/leaves")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Leaves
                </Button>
              </Tooltip>
              <Tooltip title="Document Management" placement="right">
                <Button
                  variant="text"
                  startIcon={<DocumentIcon />}
                  onClick={() => navigate("/documents")}
                  sx={{
                    justifyContent: "flex-start",
                    color: 'text.primary',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                >
                  Documents
                </Button>
              </Tooltip>
            </Stack>
          </Box>
        </Collapse>

        {/* Main content */}
        <Box component="main" sx={{ flex: 1, p: 4 }}>
          {children}
        </Box>
      </Stack>
    </Stack>
  );
}
