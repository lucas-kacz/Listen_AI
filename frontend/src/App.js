import React, { useState } from "react";
import "./App.css";

function App() {
  const [title, setTitle] = useState("Upload a file to transcribe");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileUploading, setFileUploading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [transcriptLoading, setTranscriptLoading] = useState(-1.0);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summarized, setSummarized] = useState(false);

  const backend_url = "http://localhost:5000"; //                               UNCOMMENT THIS LINE IF YOU WANT TO USE THE LOCAL BACKEND
  // const backend_url = "https://cc08-217-160-142-195.ngrok-free.app/"; //     UNCOMMENT THIS LINE IF YOU WANT TO USE THE DISTANT BACKEND

  const handleFileUpload = (event) => {
    const file = event.target.files[0];

    // File type verification
    if (file.type !== "audio/mpeg") {
      alert("Only MP3 files are allowed.");
      uploadNewFile();
      return;
    }

    // File size verification
    const maxSize = 100 * 1024 * 1024; // 100 MB
    if (file.size > maxSize) {
      alert("File size exceeds the limit of 100 MB.");
      uploadNewFile();
      return;
    }

    setSelectedFile(file);

    // Optionally, you can display a message to the user
    // indicating that the file has been uploaded successfully

    console.log("File uploaded:", file.name);
    setTitle(file.name);
  };

  const sendFileToBackend = async () => {
    setFileUploading(true);
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
      setFileUploaded(true);
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
    setFileUploading(false);
  };

  const uploadNewFile = () => {
    setSelectedFile(null);
    document.getElementById("transcript").innerHTML = "";
    document.getElementById("summary").innerHTML = "";
    setFileUploaded(false);
    setSummarized(false);
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

        // If chunk has {"result_text": in it, then append it to data
        if (chunk.includes('{"result_text":')) {
          chunk = chunk.split('{"result_text":')[1];
          chunk = chunk.substring(1, chunk.length - 2);
          data = chunk;
        } else {
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
    setSummaryLoading(true);
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
    setSummaryLoading(false);
    setSummarized(true);
  };

  return (
    <div className="App">
      <h1>
        {title}
        <span role="img" aria-label="microphone">
          🎤
        </span>
      </h1>
      {fileUploaded === false ? (
        <>
          <div
            className="drop-zone"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input type="file" onChange={handleFileUpload} />
            {selectedFile && <p>{selectedFile.name}</p>}
          </div>
          <button
            onClick={sendFileToBackend}
            style={
              fileUploading === true ? { backgroundColor: "transparent" } : {}
            }
          >
            {fileUploading === true ? (
              <>
                Uploading <i className="fa fa-spinner fa-spin"></i>
              </>
            ) : (
              <>Upload</>
            )}
          </button>
        </>
      ) : (
        <>
          <p>File uploaded</p>
          <button onClick={uploadNewFile} className="red-btn">
            Upload new file
          </button>
        </>
      )}
      <button
        onClick={transcriptFile}
        style={
          transcriptLoading >= 0.0 && transcriptLoading < 100.0
            ? { backgroundColor: "transparent" }
            : {}
        }
      >
        {transcriptLoading >= 0.0 && transcriptLoading < 100.0 ? (
          <p>
            Transcript : {transcriptLoading}%
            <i className="fa fa-spinner fa-spin"></i>
          </p>
        ) : (
          <p>Transcript</p>
        )}
        {transcriptLoading >= 0.0 && transcriptLoading < 100.0 && (
          <progress value={transcriptLoading} max="100" color="007bff" />
        )}
      </button>
      {summarized === false ? (
        <button
          onClick={summarizeFile}
          style={
            summaryLoading === true ? { backgroundColor: "transparent" } : {}
          }
        >
          {summaryLoading === true ? (
            <>
              Summarizing <i className="fa fa-spinner fa-spin"></i>
            </>
          ) : (
            <>Summarize</>
          )}
        </button>
      ) : (
        <button disabled>Summarized</button>
      )}

      <h2>Transcript</h2>
      <p id="transcript" className="paragraph"></p>
      <h2>Summary</h2>
      <p id="summary" className="paragraph"></p>
    </div>
  );
}

export default App;
