<template>
    <div>
      <video-uploader />
      <video-player />
    </div>
  </template>
  
  <script>
  import VideoUploader from '../components/video_uploader.vue';
  import VideoPlayer from '../components/video_player.vue';
  
  export default {
    components: {
      VideoUploader,
      VideoPlayer,
    },
  };
  </script>
  
