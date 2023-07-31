<template>
    <div>
      <video-uploader />
      <video-player />
    </div>
  </template>
  
  <script>
  import VideoUploader from '../components/VideoUploader.vue';
  import VideoPlayer from '../components/VideoPlayer.vue';
  
  export default {
    components: {
      VideoUploader,
      VideoPlayer,
    },
  };
  </script>
  