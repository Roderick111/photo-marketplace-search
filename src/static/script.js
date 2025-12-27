/**
 * Photo to Marketplace Search - Frontend JavaScript
 *
 * Handles image upload, API communication, and result display.
 */

// DOM Elements
const uploadArea = document.getElementById("upload-area");
const fileInput = document.getElementById("file-input");
const previewSection = document.getElementById("preview-section");
const previewImage = document.getElementById("preview-image");
const analyzeButton = document.getElementById("analyze-button");
const clearButton = document.getElementById("clear-button");
const loadingSection = document.getElementById("loading");
const resultsSection = document.getElementById("results");
const analysisInfo = document.getElementById("analysis-info");
const linksContainer = document.getElementById("links-container");
const errorSection = document.getElementById("error");
const errorMessage = document.getElementById("error-message");
const retryButton = document.getElementById("retry-button");
const backButton = document.getElementById("back-button");

// State
let selectedFile = null;

// Event Listeners
uploadArea.addEventListener("click", () => {
    // Reset value before opening dialog to ensure 'change' fires even for same file
    fileInput.value = "";
    fileInput.click();
});
uploadArea.addEventListener("dragover", handleDragOver);
uploadArea.addEventListener("dragleave", handleDragLeave);
uploadArea.addEventListener("drop", handleDrop);
fileInput.addEventListener("change", handleFileSelect);
analyzeButton.addEventListener("click", analyzeImage);
clearButton.addEventListener("click", clearSelection);
retryButton.addEventListener("click", clearSelection);
backButton.addEventListener("click", clearSelection);

/**
 * Handle dragover event for drag-and-drop.
 */
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add("dragover");
}

/**
 * Handle dragleave event for drag-and-drop.
 */
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
}

/**
 * Handle file drop event.
 */
function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove("dragover");

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

/**
 * Handle file selection from input.
 */
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

/**
 * Process selected file and show preview.
 */
function processFile(file) {
    // Validate file type
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
        showError("Please select a valid image file (JPG, PNG, or WebP).");
        return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showError("File is too large. Maximum size is 10MB.");
        return;
    }

    // Store file and show preview
    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        showPreview();
    };
    reader.readAsDataURL(file);
}

/**
 * Show the preview section.
 */
function showPreview() {
    uploadArea.classList.add("hidden");
    previewSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.add("hidden");
}

/**
 * Clear the current selection.
 */
function clearSelection() {
    selectedFile = null;
    fileInput.value = "";
    previewImage.src = "";
    uploadArea.classList.remove("hidden");
    previewSection.classList.add("hidden");
    loadingSection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.add("hidden");
}

/**
 * Analyze the selected image.
 */
async function analyzeImage() {
    if (!selectedFile) {
        showError("No image selected.");
        return;
    }

    // Show loading state
    previewSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    try {
        // Create form data
        const formData = new FormData();
        formData.append("file", selectedFile);

        // Send to API
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed");
        }

        // Display results
        displayResults(data);
    } catch (error) {
        console.error("Analysis error:", error);
        showError(error.message || "Failed to analyze image. Please try again.");
    } finally {
        loadingSection.classList.add("hidden");
    }
}

/**
 * Display analysis results.
 */
function displayResults(data) {
    const { analysis, marketplace_links, processing_time_seconds } = data;

    // Show analysis info
    analysisInfo.innerHTML = `
        <p><strong>Detected:</strong> ${analysis.description}</p>
        <p><strong>Category:</strong> ${formatCategory(analysis.object_type)}</p>
        <p><strong>Confidence:</strong> ${Math.round(analysis.confidence * 100)}%</p>
        <p><strong>Processing time:</strong> ${processing_time_seconds}s</p>
    `;

    // Generate marketplace links
    linksContainer.innerHTML = marketplace_links
        .map(
            (link) => `
            <a href="${link.url}" target="_blank" rel="noopener noreferrer" class="marketplace-link">
                <span class="marketplace-badge ${link.marketplace}">${link.marketplace}</span>
                <span class="marketplace-query">${link.query}</span>
                <span class="marketplace-arrow">→</span>
            </a>
        `
        )
        .join("");

    // Show results
    resultsSection.classList.remove("hidden");
}

/**
 * Format category name for display.
 */
function formatCategory(category) {
    const categories = {
        book: "Livre",
        clothing: "Vetement",
        electronics: "Electronique",
        furniture: "Meuble",
        tools: "Outil",
        general: "General",
    };
    return categories[category] || category;
}

/**
 * Show error message.
 */
function showError(message) {
    errorMessage.textContent = message;
    uploadArea.classList.add("hidden");
    previewSection.classList.add("hidden");
    loadingSection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    errorSection.classList.remove("hidden");
}
