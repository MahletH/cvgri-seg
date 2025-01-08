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
} from "@mui/material";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("Select a Model");

  const handleImageUpload = (event) => {
    setSelectedImage(event.target.files[0]);
    setProcessedImage(null); // Clear the processed image if a new one is uploaded
  };

  const handleSelection = (event) => { 
    setModel(event.target.value);
  }

  const handleProcessImage = async () => {
    if (!selectedImage) {
      alert("Please select an image first!");
      return;
    }

    if (model === "Select a Model") {
      alert("Please select a model first!");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImage);
    formData.append("prompt", prompt);
    formData.append("model", model) // Add the prompt to the form data

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/api/segment",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("Response received from the server:", response);
      setProcessedImage(response.data.segmented_image);
      console.log("Processed image set successfully.");
    } catch (error) {
      console.error("Error processing image:", error);
    }
  };

  return (
    <React.Fragment>
      <CssBaseline />
      <Container maxWidth="md" style={{ marginTop: "50px" }}>
        <Typography variant="h4" align="center" gutterBottom>
          Image Segmentation with CLIP
        </Typography>
        <Typography
          variant="subtitle1"
          align="center"
          color="textSecondary"
          gutterBottom
        >
          Upload an image, provide a prompt, and let CLIP Segment it for you!
        </Typography>

        <Box
          mt={4}
          display="flex"
          justifyContent="center"
          flexDirection="column"
          alignItems="center"
        >
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
            onChange={handleSelection}
            fullWidth
            style={{ marginBottom: "20px", maxWidth: "500px" }}
          > 
            <MenuItem value="Select a Model" disabled>Select a Model</MenuItem>
            <MenuItem value="clipseg">CLIPSeg</MenuItem>
            <MenuItem value="langsam">LangSAM</MenuItem>
          </Select>
          
          <Button
            variant="contained"
            color="success"
            onClick={async () => {
              setLoading(true);
              await handleProcessImage();
              setLoading(false);
            }}
            disabled={!selectedImage || loading || model === "Select a Model"}
            style={{ marginBottom: "20px" }}
          >
            {loading ? "Processing..." : "Process Image"}
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
