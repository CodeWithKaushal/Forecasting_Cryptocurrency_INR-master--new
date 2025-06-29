// Global variables
let currentChart = null;
let isLoading = false;
let lastUpdateTime = null;
let predictionStats = {};

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  // Hide loader initially
  hideLoader();

  // Add event listeners
  setupEventListeners();

  // Show initial animation
  animateElements();

  // Initialize real-time features
  initializeRealTimeFeatures();
}

function setupEventListeners() {
  // Form submission
  const form = document.querySelector(".control-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      show_plot();
    });
  }

  // Auto-generate prediction on selection change
  const ticker = document.getElementById("ticker");
  const algorithm = document.getElementById("type");

  if (ticker) {
    ticker.addEventListener("change", function () {
      if (!isLoading) {
        setTimeout(() => show_plot(), 500); // Small delay for better UX
      }
    });
  }

  if (algorithm) {
    algorithm.addEventListener("change", function () {
      if (!isLoading) {
        setTimeout(() => show_plot(), 500);
      }
    });
  }

  // Keyboard shortcuts
  document.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !isLoading) {
      show_plot();
    }
    if (e.key === "Escape" && isLoading) {
      // Allow users to cancel loading
      hideLoader();
      setLoadingState(false);
    }
  });

  // Add click-to-refresh functionality
  const chartContainer = document.getElementById("chartContainer");
  if (chartContainer) {
    chartContainer.addEventListener("dblclick", function () {
      if (!isLoading) {
        show_plot();
      }
    });
  }
}

function initializeRealTimeFeatures() {
  // Update timestamp every second
  setInterval(updateTimestamp, 1000);

  // Auto-refresh predictions every 5 minutes (if desired)
  // setInterval(() => {
  //   if (!isLoading && currentChart) {
  //     show_plot();
  //   }
  // }, 300000); // 5 minutes
}

function updateTimestamp() {
  const timestampElements = document.querySelectorAll(".timestamp");
  const now = new Date().toLocaleString();
  timestampElements.forEach((el) => (el.textContent = now));
}

function animateElements() {
  const elements = document.querySelectorAll(
    ".control-panel, .chart-container, .info-panel"
  );
  elements.forEach((el, index) => {
    setTimeout(() => {
      el.classList.add("fade-in");
    }, index * 200);
  });
}

function show_plot() {
  if (isLoading) return;

  try {
    showLoader();
    setLoadingState(true);

    const ticker = document.getElementById("ticker").value;
    const algorithm = document.getElementById("type").value;

    // Validate inputs
    if (!ticker || !algorithm) {
      showError("Please select both ticker and algorithm");
      hideLoader();
      setLoadingState(false);
      return;
    }

    // Update status with enhanced feedback
    updateStatus(
      "loading",
      `🔄 Analyzing ${ticker} using ${algorithm} algorithm...`
    );

    // Clear previous chart with animation
    if (currentChart) {
      const chartContainer = document.getElementById("chartContainer");
      if (chartContainer) {
        chartContainer.style.opacity = "0.5";
        setTimeout(() => {
          currentChart.destroy();
          currentChart = null;
          chartContainer.style.opacity = "1";
        }, 300);
      }
    }

    // Clear info panel with animation
    clearInfoPanel();

    // Add progress simulation
    simulateProgress();

    // Fetch data and create chart
    fetchDataAndCreateChart(ticker, algorithm);
  } catch (error) {
    console.error("Error in show_plot:", error);
    showError("An error occurred while generating the prediction");
    hideLoader();
    setLoadingState(false);
  }
}

function simulateProgress() {
  const progressBar = document.getElementById("progressBar");
  if (progressBar) {
    progressBar.style.width = "0%";
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 90) {
        progress = 90;
        clearInterval(interval);
      }
      progressBar.style.width = progress + "%";
    }, 200);

    // Complete progress when loading finishes
    setTimeout(() => {
      progressBar.style.width = "100%";
      clearInterval(interval);
    }, 3000);
  }
}

function fetchDataAndCreateChart(ticker, algorithm) {
  const url = `http://127.0.0.1:5000/getJson/${ticker}/${algorithm}`;
  const startTime = Date.now();

  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const endTime = Date.now();
      const processingTime = ((endTime - startTime) / 1000).toFixed(2);

      if (data.error) {
        throw new Error(data.error);
      }

      hideLoader();
      setLoadingState(false);

      // Enhanced success message
      updateStatus("success", `✅ Prediction completed in ${processingTime}s`);

      // Store prediction stats
      predictionStats = {
        ticker: ticker,
        algorithm: algorithm,
        processingTime: processingTime,
        timestamp: new Date(),
        dataPoints: data[0] ? data[0].length : 0,
        predictionPoints: data[1] ? data[1].length : 0,
      };

      createChart(data, ticker, algorithm);
      updateInfoPanel(data, algorithm);

      // Add success animation
      const chartContainer = document.querySelector(".chart-container");
      if (chartContainer) {
        chartContainer.classList.add("slide-up");
        setTimeout(() => chartContainer.classList.remove("slide-up"), 600);
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
      hideLoader();
      setLoadingState(false);

      // Enhanced error handling
      let errorMessage = "Failed to fetch data";
      let suggestion = "Please try again in a few moments";

      if (error.message.includes("500")) {
        errorMessage = "Server error - insufficient data";
        suggestion =
          "Try a different cryptocurrency (BTC-USD, ETH-USD work best)";
      } else if (error.message.includes("400")) {
        errorMessage = "Invalid request";
        suggestion = "Check your internet connection and try again";
      } else if (error.message.includes("Failed to fetch")) {
        errorMessage = "Network connection error";
        suggestion = "Check your internet connection";
      }

      updateStatus("error", `❌ ${errorMessage}`);
      showError(`${errorMessage}: ${error.message}`, suggestion);
    });
}

function createChart(data, ticker, algorithm) {
  const dataPoints = [];
  const predPoints = [];

  // Process historical data
  if (data[0] && Array.isArray(data[0])) {
    data[0].forEach((point) => {
      dataPoints.push({
        x: new Date(point.date),
        y: Number(point.close),
      });
    });
  }

  // Process prediction data
  if (data[1] && Array.isArray(data[1])) {
    data[1].forEach((point) => {
      predPoints.push({
        x: new Date(point.date),
        y: Number(point.close),
      });
    });
  }

  // Calculate price statistics
  const prices = dataPoints.map((p) => p.y);
  const currentPrice = prices[prices.length - 1];
  const predictionPrices = predPoints.map((p) => p.y);
  const avgPrediction =
    predictionPrices.reduce((a, b) => a + b, 0) / predictionPrices.length;
  const priceChange = (
    ((avgPrediction - currentPrice) / currentPrice) *
    100
  ).toFixed(2);

  const chartOptions = {
    exportEnabled: true,
    animationEnabled: true,
    zoomEnabled: true,
    theme: "light2",
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    title: {
      text: `${ticker} - ${algorithm} Price Prediction`,
      fontSize: 28,
      fontWeight: "bold",
      fontColor: "#2563eb",
      fontFamily: "Inter, sans-serif",
      margin: 25,
    },
    subtitles: [
      {
        text: `Current: $${
          currentPrice?.toFixed(2) || "N/A"
        } | Predicted Avg: $${avgPrediction.toFixed(
          2
        )} | Change: ${priceChange}%`,
        fontSize: 16,
        fontColor: priceChange >= 0 ? "#10b981" : "#ef4444",
        fontWeight: "600",
      },
      {
        text: `Algorithm: ${algorithm} | Processing Time: ${
          predictionStats.processingTime || "N/A"
        }s | Last Updated: ${new Date().toLocaleString()}`,
        fontSize: 14,
        fontColor: "#6b7280",
      },
    ],
    axisX: {
      title: "Time",
      titleFontSize: 16,
      titleFontColor: "#374151",
      titleFontWeight: "600",
      valueFormatString: "DD MMM HH:mm",
      labelFontColor: "#6b7280",
      labelFontSize: 12,
      gridColor: "#e5e7eb",
      gridThickness: 1,
      tickColor: "#d1d5db",
      tickThickness: 1,
    },
    axisY: {
      title: "Price (USD)",
      titleFontSize: 16,
      titleFontColor: "#374151",
      titleFontWeight: "600",
      labelFontColor: "#6b7280",
      labelFontSize: 12,
      gridColor: "#e5e7eb",
      gridThickness: 1,
      tickColor: "#d1d5db",
      tickThickness: 1,
      prefix: "$",
      valueFormatString: "#,##0.00",
    },
    legend: {
      horizontalAlign: "center",
      verticalAlign: "top",
      fontSize: 16,
      fontColor: "#374151",
      fontWeight: "600",
      cursor: "pointer",
      itemclick: function (e) {
        if (
          typeof e.dataSeries.visible === "undefined" ||
          e.dataSeries.visible
        ) {
          e.dataSeries.visible = false;
        } else {
          e.dataSeries.visible = true;
        }
        e.chart.render();
      },
    },
    charts: [
      {
        data: [
          {
            type: "spline",
            name: "📈 Historical Data",
            showInLegend: true,
            color: "#2563eb",
            lineThickness: 4,
            markerSize: 0,
            xValueFormatString: "DD MMM YYYY HH:mm",
            yValueFormatString: "$#,##0.00",
            dataPoints: dataPoints,
          },
          {
            type: "spline",
            name: `🔮 ${algorithm} Prediction`,
            showInLegend: true,
            color: "#dc2626",
            lineThickness: 4,
            lineDashType: "dash",
            markerSize: 8,
            markerType: "circle",
            markerColor: "#dc2626",
            markerBorderColor: "#ffffff",
            markerBorderThickness: 2,
            xValueFormatString: "DD MMM YYYY HH:mm",
            yValueFormatString: "$#,##0.00",
            dataPoints: predPoints,
          },
        ],
      },
    ],
    toolTip: {
      shared: true,
      backgroundColor: "#ffffff",
      borderColor: "#e5e7eb",
      borderThickness: 2,
      fontColor: "#374151",
      fontSize: 14,
      cornerRadius: 8,
      animationEnabled: true,
    },
    crosshair: {
      enabled: true,
      snapToDataPoint: true,
      color: "#6b7280",
      thickness: 1,
      lineDashType: "dot",
    },
  };

  currentChart = new CanvasJS.StockChart("chartContainer", chartOptions);
  currentChart.render();

  // Add animation to chart container
  const chartContainer = document.querySelector(".chart-container");
  chartContainer.classList.add("slide-up");

  // Store current data for potential export
  window.chartData = {
    ticker,
    algorithm,
    historical: dataPoints,
    predictions: predPoints,
    stats: data[2] || {},
  };
}

function updateInfoPanel(data, algorithm) {
  let rmse = "N/A";
  let accuracy = "N/A";
  let historicalPoints = 0;
  let predictionPoints = 0;

  // Extract metrics if available
  if (data[2]) {
    if (data[2].rmse) {
      rmse = data[2].rmse.toFixed(4);
    }
    if (data[2].historical_points) {
      historicalPoints = data[2].historical_points;
    }
    if (data[2].prediction_points) {
      predictionPoints = data[2].prediction_points;
    }

    // Calculate approximate accuracy (this is a simplified calculation)
    const avgPrice = data[0]
      ? data[0].reduce((sum, point) => sum + Number(point.close), 0) /
        data[0].length
      : 0;
    if (avgPrice > 0 && data[2].rmse) {
      accuracy =
        Math.max(0, 100 - (data[2].rmse / avgPrice) * 100).toFixed(2) + "%";
    }
  }

  const infoPanel = document.querySelector(".info-panel");
  if (infoPanel) {
    infoPanel.innerHTML = `
            <div class="info-card primary fade-in">
                <div class="info-card-icon">🤖</div>
                <div class="info-card-title">Algorithm Used</div>
                <div class="info-card-value">${algorithm}</div>
            </div>
            <div class="info-card ${
              rmse !== "N/A" ? "success" : "warning"
            } fade-in">
                <div class="info-card-icon">📊</div>
                <div class="info-card-title">RMSE Score</div>
                <div class="info-card-value">${rmse}</div>
            </div>
            <div class="info-card ${
              accuracy !== "N/A" ? "primary" : "warning"
            } fade-in">
                <div class="info-card-icon">🎯</div>
                <div class="info-card-title">Accuracy</div>
                <div class="info-card-value">${accuracy}</div>
            </div>
            <div class="info-card success fade-in">
                <div class="info-card-icon">📈</div>
                <div class="info-card-title">Data Points</div>
                <div class="info-card-value">${historicalPoints}</div>
            </div>
        `;
  }
}

function clearInfoPanel() {
  const infoPanel = document.querySelector(".info-panel");
  if (infoPanel) {
    infoPanel.innerHTML = "";
  }
}

function showLoader() {
  const loader = document.getElementById("loader");
  const loadingOverlay = document.getElementById("loadingOverlay");

  if (loader) {
    loader.style.display = "block";
  }

  if (loadingOverlay) {
    loadingOverlay.classList.add("show");
  }
}

function hideLoader() {
  const loader = document.getElementById("loader");
  const loadingOverlay = document.getElementById("loadingOverlay");

  if (loader) {
    loader.style.display = "none";
  }

  if (loadingOverlay) {
    loadingOverlay.classList.remove("show");
  }
}

function setLoadingState(loading) {
  isLoading = loading;
  const button = document.querySelector(".btn-primary");
  const selects = document.querySelectorAll(".form-select");

  if (button) {
    button.disabled = loading;
    button.textContent = loading ? "Generating..." : "Generate Prediction";
  }

  selects.forEach((select) => {
    select.disabled = loading;
  });
}

function updateStatus(type, message) {
  let statusEl = document.querySelector(".status-indicator");

  if (!statusEl) {
    statusEl = document.createElement("div");
    statusEl.className = "status-indicator";

    const controlPanel = document.querySelector(".control-panel");
    if (controlPanel) {
      controlPanel.appendChild(statusEl);
    }
  }

  // Remove previous status classes
  statusEl.classList.remove("status-success", "status-error", "status-loading");

  // Add new status class
  statusEl.classList.add(`status-${type}`);
  statusEl.textContent = message;

  // Auto-hide success messages after 5 seconds
  if (type === "success") {
    setTimeout(() => {
      if (statusEl && statusEl.classList.contains("status-success")) {
        statusEl.style.opacity = "0";
        setTimeout(() => statusEl.remove(), 300);
      }
    }, 5000);
  }
}

function showError(message) {
  console.error("Error:", message);

  // Create or update error banner
  let errorBanner = document.querySelector(".error-banner");
  if (!errorBanner) {
    errorBanner = document.createElement("div");
    errorBanner.className = "error-banner";

    const controlPanel = document.querySelector(".control-panel");
    if (controlPanel) {
      controlPanel.appendChild(errorBanner);
    }
  }

  errorBanner.innerHTML = `
    <div class="error-icon">⚠️</div>
    <div class="error-content">
      <div class="error-title">Prediction Error</div>
      <div class="error-message">${message}</div>
      <div class="error-suggestion">Please try a different cryptocurrency or check your internet connection.</div>
    </div>
  `;

  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (errorBanner && errorBanner.parentNode) {
      errorBanner.parentNode.removeChild(errorBanner);
    }
  }, 10000);
}

// Utility function to format currency
function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

// Utility function to format date
function formatDate(date) {
  return new Intl.DateTimeFormat("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}
