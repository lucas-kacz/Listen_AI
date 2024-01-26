import React, { useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [transcriptLoading, setTranscriptLoading] = useState(-1.0);

  const backend_url2 = "http://localhost:5000";
  const backend_url = "http://217.160.142.195:25000";

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

      const response = await fetch(backend_url + "/upload", {
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
      setTranscriptLoading(0.0);

      // Use the selectedFile state variable to retrieve the file
      const file = selectedFile.name;
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(backend_url + "/transcript", {
        method: "POST",
        body: formData,
      });

      var data = "";

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8"); // Use the appropriate encoding

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          setTranscriptLoading(100.0);
          console.log("Stream complete");
          break;
        }

        // Convert the Uint8Array to a string
        var chunk = decoder.decode(value);

        // If chunk starts with {"result_text":, then append it to data
        if (chunk.startsWith('{"result_text":')) {
          chunk = chunk.substring(17, chunk.length - 2);
          data = chunk;
        } else {
          // Handle each chunk of data, for example, log it to the console
          console.log(parseFloat(chunk).toFixed(1));
          setTranscriptLoading(parseFloat(chunk).toFixed(1));
        }
      }

      // Handle the response from the server
      console.log(data);

      document.getElementById("transcript").style.display = "block";
      document.getElementById("transcript").innerHTML = data;
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

      const response = await fetch(backend_url + "/summary", {
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
      <button
        onClick={transcriptFile}
        style={
          transcriptLoading >= 0.0 && transcriptLoading < 100.0
            ? { backgroundColor: "transparent" }
            : {}
        }
      >
        {transcriptLoading >= 0.0 && transcriptLoading < 100.0 ? (
          <p>Transcript : {transcriptLoading}%</p>
        ) : (
          <p>Transcript</p>
        )}
        {transcriptLoading >= 0.0 && transcriptLoading < 100.0 && (
          <progress value={transcriptLoading} max="100" color="007bff" />
        )}
      </button>
      <button onClick={summarizeFile}>Summarize</button>
      <h2>Transcript</h2>
      <p id="transcript" className="paragraph"></p>
      <h2>Summary</h2>
      <p id="summary" className="paragraph"></p>
    </div>
  );
}

export default App;
