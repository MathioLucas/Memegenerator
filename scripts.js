document.getElementById("imageUpload").addEventListener("change", handleImagePreview);
document.getElementById("uploadForm").addEventListener("submit", handleFormSubmit);

async function handleFormSubmit(event) {
    event.preventDefault();

    const imageInput = document.getElementById("imageUpload");
    const captionInput = document.getElementById("caption");

    // Validate input
    if (!imageInput.files.length) {
        alert("Please upload an image.");
        return;
    }

    const formData = new FormData();
    formData.append("file", imageInput.files[0]);
    formData.append("caption", captionInput.value);

    try {
        const response = await fetch("/upload/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            alert("Failed to upload image.");
            return;
        }

        const result = await response.text();  // Get the HTML response from the server
        document.getElementById("resultContainer").innerHTML = result;  // Insert the result into the container
    } catch (error) {
        console.error("Error uploading meme:", error);
        alert("Error uploading meme.");
    }
}

function handleImagePreview(event) {
    const previewContainer = document.getElementById("imagePreview");
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onloadend = function () {
        const img = document.createElement("img");
        img.src = reader.result;
        img.style.maxWidth = "100%";
        previewContainer.innerHTML = ''; // Clear any previous preview
        previewContainer.appendChild(img);
    };

    if (file) {
        reader.readAsDataURL(file);
    }
}




