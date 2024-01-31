import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [title, setTitle] = useState("ListenAI");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileUploading, setFileUploading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [transcriptLoading, setTranscriptLoading] = useState(-1.0);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summarized, setSummarized] = useState(false);
  const [backend_url, setBackendUrl] = useState(
    process.env.REACT_APP_DISTANT_URL
  );
  const [files, setFiles] = useState([]);

  const localUrl = process.env.REACT_APP_LOCAL_URL;
  const distantUrl = process.env.REACT_APP_DISTANT_URL;

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
    document.getElementById("transcript").style.display = "none";
    document.getElementById("transcript").innerHTML = "";
    document.getElementById("summary").style.display = "none";
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
      const decoder = new TextDecoder("utf-32"); // Use the appropriate encoding

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

  const useLocalBackend = () => {
    setBackendUrl(localUrl);
  };

  const useDistantBackend = () => {
    setBackendUrl(distantUrl);
  };

  const getAllLocalFiles = async () => {
    try {
      const response = await fetch(backend_url + "/files", {
        method: "GET",
      });

      const data = await response.json();

      // Handle the response from the server
      console.log(data);

      setFiles(data.files);
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  const openFile = async (file) => {
    try {
      const response = await fetch(
        backend_url + "/transcript/" + file.split(".mp3")[0]
      );

      const data = await response.json();

      // Handle the response from the server
      console.log(data);

      document.getElementById("transcript").style.display = "block";
      document.getElementById("transcript").innerHTML = data.result_text;

      document.getElementById("summary").style.display = "none";
      document.getElementById("summary").innerHTML = "";

      setSummarized(false);
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  const deleteFile = async (file) => {
    try {
      const response = await fetch(
        backend_url + "/delete/" + file.split(".mp3")[0]
      );

      const data = await response.json();

      // Handle the response from the server
      console.log(data);

      getAllLocalFiles();
    } catch (error) {
      // Handle any errors
      console.error(error);
    }
  };

  useEffect(() => {
    getAllLocalFiles();
    // eslint-disable-next-line
  }, []);

  return (
    <div className="App">
      <div className="side-container">
        <h2>Available Files</h2>
        <ul>
          {files.length > 0 &&
            files.map((file, index) => {
              return (
                <li key={index} title={file} onClick={() => openFile(file)}>
                  {file.split(".mp3")[0].length < 25
                    ? file.split(".mp3")[0]
                    : file.split(".mp3")[0].substring(0, 25) + " [...]"}
                  <button onClick={() => deleteFile(file)}>
                    <i className="fa fa-trash-o"></i>
                  </button>
                </li>
              );
            })}
        </ul>
      </div>
      <div className="main-container">
        <h1>
          {title}
          <span role="img" aria-label="microphone">
            🎤
          </span>
        </h1>
        <h2>Transcript</h2>
        <p id="transcript" className="paragraph"></p>
        <p className="spacer50"></p>
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
        <h2>Summary</h2>
        <p id="summary" className="paragraph"></p>
      </div>
      <div className="upload-container">
        <h2>Add a new file</h2>
        <p>
          The backend in use is: <b>{backend_url}</b>
        </p>
        <div className="flex-container">
          {backend_url === "http://localhost:5000" ? (
            <button className="flex-item" onClick={useDistantBackend}>
              Use distant backend
            </button>
          ) : (
            <button className="flex-item" onClick={useLocalBackend}>
              Use local backend
            </button>
          )}
        </div>
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
      </div>
    </div>
  );
}

export default App;
