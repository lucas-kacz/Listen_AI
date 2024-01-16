import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Optionally, you can display a message to the user
    // indicating that the file has been uploaded successfully

    console.log("File uploaded:", file.name);
  };

  const sendFileToBackend = async () => {
    try {
      // Use the selectedFile state variable to retrieve the file
      const file = selectedFile;
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:5000/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      // Handle the response from the server
      console.log(data);
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  const transcriptFile = async () => {
    try {
      // Use the selectedFile state variable to retrieve the file
      const file = selectedFile.name;
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:5000/transcript", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      // Handle the response from the server
      console.log(data);

      document.getElementById("transcript").style.display = "block";
      document.getElementById("transcript").innerHTML = data.result_text;
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    setSelectedFile(file);
    console.log("File uploaded:", file.name);
  };

  const summarizeFile = async () => {
    try {
      // Use the selectedFile state variable to retrieve the file
      const text = document.getElementById("transcript").innerText;
      const formData = new FormData();
      formData.append("file", text);

      const response = await fetch("http://localhost:5000/summary", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      // Handle the response from the server
      console.log(data);

      document.getElementById("summary").style.display = "block";
      document.getElementById("summary").innerHTML = data.summary;
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  return (
    <div className="App">
      <h1>
        Upload a file to transcribe
        <span role="img" aria-label="microphone">
          🎤
        </span>
      </h1>
      <div
        className="drop-zone"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input type="file" onChange={handleFileUpload} />
        {selectedFile && <p>{selectedFile.name}</p>}
      </div>
      <button onClick={sendFileToBackend}>Send to Backend</button>
      <button onClick={transcriptFile}>Transcript</button>
      <button onClick={summarizeFile}>Summarize</button>
      <h2>Transcript</h2>
      <p id="transcript"></p>
      <h2>Summary</h2>
      <p id="summary"></p>
    </div>
  );
}

export default App;
