<script setup>
import { ref } from 'vue'
import { uploadFile } from '../api.js'

const emit = defineEmits(['uploaded'])
const uploading = ref(false)
const message = ref('')

async function handleFiles(e) {
  const files = e.target.files || e.dataTransfer?.files
  if (!files?.length) return

  uploading.value = true
  message.value = ''

  for (const file of files) {
    try {
      const result = await uploadFile(file)
      message.value = `✅ ${result.message}`
      emit('uploaded', result)
    } catch (err) {
      message.value = `❌ ${err.message}`
    }
  }
  uploading.value = false
  e.target.value = '' // 重置 input
}

function onDrop(e) {
  e.preventDefault()
  handleFiles(e)
}
</script>

<template>
  <div
    class="border border-dashed border-gray-600 rounded-lg p-4 text-center
           hover:border-blue-500 transition-colors cursor-pointer"
    @drop="onDrop"
    @dragover.prevent
  >
    <label class="cursor-pointer">
      <input
        type="file"
        accept=".md,.txt,.pdf,.docx"
        multiple
        class="hidden"
        @change="handleFiles"
      />
      <div class="text-gray-400 text-sm">
        <span v-if="uploading">⏳ 上传中...</span>
        <span v-else>📎 点击或拖拽上传文档（.md / .txt / .pdf / .docx）</span>
      </div>
    </label>
    <div v-if="message" class="mt-2 text-xs" :class="message.startsWith('✅') ? 'text-green-400' : 'text-red-400'">
      {{ message }}
    </div>
  </div>
</template>
