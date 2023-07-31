<template>
    <div>
      <input type="file" @change="onFileChange" accept="video/*" />
      <button @click="uploadVideo" :disabled="uploading">Upload</button>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        videoFile: null,
        uploading: false,
      };
    },
    methods: {
      onFileChange(event) {
        this.videoFile = event.target.files[0];
      },
      async uploadVideo() {
        this.uploading = true;
        const formData = new FormData();
        formData.append('video', this.videoFile);
  
        try {
          // Send video to Flask backend for processing
          const response = await axios.post('/api/upload', formData);
          // Handle the response if needed (e.g., show success message)
        } catch (error) {
          console.error('Error uploading video:', error);
        } finally {
          this.uploading = false;
        }
      },
    },
  };
  </script>
  