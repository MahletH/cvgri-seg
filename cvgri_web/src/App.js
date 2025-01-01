import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);

  const handleImageUpload = (e) => {
    setImage(URL.createObjectURL(e.target.files[0]));
  };

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append('image', document.querySelector('input[type="file"]').files[0]);
    formData.append('prompt', prompt);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/segment', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Get the URL of the segmented image
      setResult(response.data.segmentedImage);
    } catch (error) {
      console.error("Error during segmentation", error);
    }
  };

  return (
    <div className="container">
      <h1>Zero-Shot Image Segmentation</h1>
      <div className="mb-3">
        <input type="file" onChange={handleImageUpload} />
      </div>
      <div className="mb-3">
        <input type="text" value={prompt} onChange={handlePromptChange} placeholder="Enter your prompt" />
      </div>
      <div className="mb-3">
        <button className="btn btn-primary" onClick={handleSubmit}>Segment Image</button>
      </div>

      {result && <div className="mt-3">
        <h3>Segmented Image</h3>
        <img src={`http://127.0.0.1:5000/${result}`} alt="Segmented Result" />
      </div>}
    </div>
  );
};

export default App;
