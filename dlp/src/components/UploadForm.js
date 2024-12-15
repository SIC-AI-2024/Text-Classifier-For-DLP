import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  LinearProgress,
  Typography,
  Paper,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Alert,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";

const UploadForm = () => {
  const [text, setText] = useState("");
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const newFiles = selectedFiles.map((file) => ({
      file,
      id: Math.random().toString(36).substring(7),
      progress: 0,
    }));

    setFiles((prevFiles) => [...prevFiles, ...newFiles]);

    // Simulate upload progress for each new file
    newFiles.forEach((fileObj) => {
      simulateUpload(fileObj.id);
    });
  };

  const simulateUpload = (fileId) => {
    const interval = setInterval(() => {
      setFiles((prevFiles) => {
        const updatedFiles = prevFiles.map((f) => {
          if (f.id === fileId) {
            const newProgress = Math.min(f.progress + 10, 100);
            if (newProgress === 100) {
              clearInterval(interval);
            }
            return { ...f, progress: newProgress };
          }
          return f;
        });
        return updatedFiles;
      });
    }, 500);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();

      // Add text if present
      if (text.trim()) {
        formData.append("text", text);
      }

      // Add files if present
      files.forEach((fileObj, index) => {
        formData.append("files", fileObj.file);
      });

      const response = await fetch("http://localhost:8000/extract-text/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.classification);
    } catch (err) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const removeFile = (fileId) => {
    setFiles((prevFiles) => prevFiles.filter((f) => f.id !== fileId));
  };

  const getTotalProgress = () => {
    if (files.length === 0) return 0;
    const totalProgress = files.reduce((sum, file) => sum + file.progress, 0);
    return Math.round(totalProgress / files.length);
  };

  const renderResults = () => {
    if (!results) return null;

    let items = [];
    let currentIndex = 0;

    // Add text result if text was submitted
    if (text.trim()) {
      items.push(
        <ListItem
          key="text-result"
          sx={{
            bgcolor: "background.paper",
            mb: 1,
            borderRadius: 1,
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          <ListItemText
            primary="Text Input"
            secondary={
              <Typography
                color={results[currentIndex] ? "error.main" : "success.main"}
                sx={{ mt: 1 }}
              >
                Classification: {results[currentIndex] ? "Sensitive" : "Safe"}
              </Typography>
            }
          />
        </ListItem>
      );
      currentIndex++;
    }

    // Add file results
    files.forEach((fileObj, index) => {
      items.push(
        <ListItem
          key={fileObj.id}
          sx={{
            bgcolor: "background.paper",
            mb: 1,
            borderRadius: 1,
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          <ListItemText
            primary={fileObj.file.name}
            secondary={
              <Typography
                color={
                  results[currentIndex + index] ? "error.main" : "success.main"
                }
                sx={{ mt: 1 }}
              >
                Classification:{" "}
                {results[currentIndex + index] ? "Sensitive" : "Safe"}
              </Typography>
            }
          />
        </ListItem>
      );
    });

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Results:
        </Typography>
        <List>{items}</List>
      </Box>
    );
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: "auto" }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={4}
          variant="outlined"
          label="Enter your text"
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setResults(null);
          }}
        />
      </Box>

      <Box sx={{ mb: 3 }}>
        <input
          accept="*/*"
          style={{ display: "none" }}
          id="file-upload"
          type="file"
          multiple
          onChange={handleFileChange}
        />
        <label htmlFor="file-upload">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
          >
            Upload Files
          </Button>
        </label>

        {files.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Total Progress: {getTotalProgress()}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={getTotalProgress()}
              sx={{ mb: 2 }}
            />

            <List>
              {files.map((fileObj) => (
                <ListItem
                  key={fileObj.id}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => removeFile(fileObj.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                  sx={{
                    bgcolor: "background.paper",
                    mb: 1,
                    borderRadius: 1,
                    border: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <ListItemText
                    primary={fileObj.file.name}
                    secondary={
                      <Box sx={{ width: "100%" }}>
                        <LinearProgress
                          variant="determinate"
                          value={fileObj.progress}
                          sx={{ mt: 1 }}
                        />
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mt: 0.5 }}
                        >
                          {fileObj.progress}% uploaded
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </Box>

      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={handleSubmit}
        disabled={(!text && files.length === 0) || isLoading}
      >
        {isLoading ? "Processing..." : "Process"}
      </Button>

      {renderResults()}
    </Paper>
  );
};

export default UploadForm;
