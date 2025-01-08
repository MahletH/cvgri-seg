import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Button,
  TextField,
  Box,
  Card,
  CardContent,
  CardMedia,
  Grid,
  CssBaseline,
  Select,
  MenuItem,
  CircularProgress,
} from "@mui/material";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("");

  const API_URL = "http://127.0.0.1:5000/api/segment";

  const handleImageUpload = (event) => {
    setSelectedImage(event.target.files[0]);
    setProcessedImage(null);
  };

  const handleProcessImage = async () => {
    if (!selectedImage || !model) {
      alert("Please ensure both an image and a model are selected!");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImage);
    formData.append("prompt", prompt);
    formData.append("model", model);

    setLoading(true);
    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setProcessedImage(response.data.segmented_image);
    } catch (error) {
      console.error("Error processing image:", error);
      alert(error.response?.data?.error || "An error occurred while processing the image.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <React.Fragment>
      <CssBaseline />
      <Container maxWidth="md" style={{ marginTop: "50px" }}>
        <Typography variant="h4" align="center" gutterBottom>
          Language Guided Image Segmentation
        </Typography>
        <Typography
          variant="subtitle1"
          align="center"
          color="textSecondary"
          gutterBottom
        >
          Upload an image, provide a prompt, and let the model segment it for you!
        </Typography>

        <Box mt={4} display="flex" flexDirection="column" alignItems="center">
          <Button
            variant="contained"
            component="label"
            color="primary"
            style={{ marginBottom: "20px" }}
          >
            Upload Image
            <input
              type="file"
              hidden
              accept="image/*"
              onChange={handleImageUpload}
            />
          </Button>

          <TextField
            label="Enter a Prompt (Optional)"
            variant="outlined"
            fullWidth
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            style={{ marginBottom: "20px", maxWidth: "500px" }}
          />

          <Select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            displayEmpty
            fullWidth
            style={{ marginBottom: "20px", maxWidth: "500px" }}
          >
            <MenuItem value="" disabled>
              Select a Model
            </MenuItem>
            <MenuItem value="clipseg">CLIPSeg</MenuItem>
            <MenuItem value="langsam">LangSAM</MenuItem>
          </Select>

          <Button
            variant="contained"
            color="success"
            onClick={handleProcessImage}
            disabled={!selectedImage || loading || !model}
            style={{ marginBottom: "20px" }}
          >
            {loading ? <CircularProgress size={24} /> : "Process Image"}
          </Button>
        </Box>

        <Grid container spacing={4} justifyContent="center" alignItems="center">
          {selectedImage && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" align="center">
                    Uploaded Image
                  </Typography>
                  <CardMedia
                    component="img"
                    image={URL.createObjectURL(selectedImage)}
                    alt="Uploaded"
                    style={{ maxHeight: "300px", objectFit: "contain" }}
                  />
                </CardContent>
              </Card>
            </Grid>
          )}

          {processedImage && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" align="center">
                    Processed Image
                  </Typography>
                  <CardMedia
                    component="img"
                    image={processedImage}
                    alt="Processed"
                    style={{ maxHeight: "300px", objectFit: "contain" }}
                  />
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Container>
    </React.Fragment>
  );
}

export default App;
