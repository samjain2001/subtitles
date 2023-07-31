<template>
    <div>
      <video ref="videoPlayer" controls :src="videoUrl"></video>
      <div v-if="subtitleData">
        <div v-for="subtitle in subtitleData" :key="subtitle.index" class="subtitle">
          {{ subtitle.text }}
        </div>
      </div>
      <button @click="downloadVideo" :disabled="downloading">Download Processed Video</button>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        videoUrl: '', // Video URL to be fetched from Flask backend
        subtitleData: null,
        downloading: false,
      };
    },
    async mounted() {
      // Fetch video URL and subtitle data from Flask backend
      this.videoUrl = await this.fetchVideoUrl();
      this.subtitleData = await this.fetchSubtitleData();
    },
    methods: {
      async fetchVideoUrl() {
        try {
          // Fetch video URL from Flask backend
          const response = await axios.get('/api/video_url');
          return response.data.videoUrl;
        } catch (error) {
          console.error('Error fetching video URL:', error);
          return '';
        }
      },
      async fetchSubtitleData() {
        try {
          // Fetch subtitle data from Flask backend
          const response = await axios.get('/api/subtitles');
          return response.data;
        } catch (error) {
          console.error('Error fetching subtitle data:', error);
          return null;
        }
      },
      async downloadVideo() {
        this.downloading = true;
        try {
          // Download processed video from Flask backend
          const response = await axios.get('/api/download', { responseType: 'blob' });
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'processed_video.mp4');
          document.body.appendChild(link);
          link.click();
        } catch (error) {
          console.error('Error downloading video:', error);
        } finally {
          this.downloading = false;
        }
      },
    },
  };
  </script>
  
  <style>
  /* Add any custom styles for the video player and subtitles here */
  .subtitle {
    position: absolute;
    color: yellow;
    font-size: 24px;
    /* Set the position based on your requirements */
    /* Example: bottom: 10px; left: 50%; transform: translateX(-50%); */
  }
  </style>
  