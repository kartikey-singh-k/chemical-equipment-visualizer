import React, { useState, useEffect } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const App = () => {
  const [file, setFile] = useState(null);
  const [stats, setStats] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("https://chem-backend-rnle.onrender.com/api/history/");
      setHistory(res.data);
    } catch (err) { console.error(err); }
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a CSV file first!");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("https://chem-backend-rnle.onrender.com/api/analyze/", formData);
      setStats(res.data.stats);
      setTableData(res.data.data);
      fetchHistory(); // Refresh history
    } catch (err) {
      alert("Error analyzing file.");
    }
  };

  const downloadPDF = async () => {
    if(!stats) return;
    try {
        const res = await axios.post("https://chem-backend-rnle.onrender.com/api/report/", stats, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'report.pdf');
        document.body.appendChild(link);
        link.click();
    } catch(err) { console.error(err); }
  }

  // Chart Data Configuration
  const chartData = stats ? {
    labels: Object.keys(stats.type_distribution),
    datasets: [{
      label: 'Equipment Count',
      data: Object.values(stats.type_distribution),
      backgroundColor: 'rgba(53, 162, 235, 0.5)',
    }],
  } : null;

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>⚗️ Chemical Equipment Visualizer</h1>
      
      {/* Upload Section */}
      <div style={{ marginBottom: "20px", padding: "15px", border: "1px solid #ddd" }}>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload} style={{ marginLeft: "10px", padding: "5px 15px" }}>Analyze CSV</button>
      </div>

      {/* Main Dashboard */}
      {stats && (
        <div style={{ display: "flex", gap: "20px" }}>
          <div style={{ flex: 1 }}>
            <h3>Summary Statistics</h3>
            <ul>
              <li>Total Count: {stats.total_count}</li>
              <li>Avg Pressure: {stats.avg_pressure}</li>
              <li>Avg Temp: {stats.avg_temp}</li>
              <li>Avg Flow: {stats.avg_flow}</li>
            </ul>
            <button onClick={downloadPDF}>Download PDF Report</button>
            <div style={{ marginTop: "20px" }}>
                <Bar data={chartData} />
            </div>
          </div>

          <div style={{ flex: 1, maxHeight: "500px", overflowY: "scroll" }}>
            <h3>Data Preview</h3>
            <table border="1" cellPadding="5" style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Flow</th>
                  <th>Pressure</th>
                  <th>Temp</th> {/* <--- Added Header */}
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, i) => (
                  <tr key={i}>
                    <td>{row["Equipment Name"]}</td>
                    <td>{row["Type"]}</td>
                    <td>{row["Flowrate"]}</td>
                    <td>{row["Pressure"]}</td>
                    <td>{row["Temperature"]}</td> {/* <--- Added Data Row */}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* History Section */}
      <div style={{ marginTop: "40px" }}>
        <h3>📂 Recent Uploads</h3>
        {history.map((h) => (
            <div key={h.id} style={{padding: "5px", borderBottom: "1px solid #eee"}}>
                {new Date(h.uploaded_at).toLocaleString()} - <strong>{h.filename}</strong>
            </div>
        ))}
      </div>
    </div>
  );
};

export default App;