<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getDocuments } from '../api.js'
import FileUpload from './FileUpload.vue'

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  currentSession: { type: String, default: '' },
})
const emit = defineEmits(['selectSession', 'newSession'])

const documents = ref([])
const showDocs = ref(false)
const docsPanel = ref(null)
const panelHeight = ref(0)

async function refreshDocs() {
  try {
    const data = await getDocuments()
    documents.value = data.documents || []
  } catch {}
}

async function toggleDocs() {
  if (!showDocs.value) {
    // 展开：先渲染内容获取高度，再动画展开
    showDocs.value = true
    refreshDocs()
    await nextTick()
    panelHeight.value = docsPanel.value?.scrollHeight || 0
  } else {
    // 收起：先设高度为当前值，再动画到 0
    panelHeight.value = 0
    setTimeout(() => { showDocs.value = false }, 300)
  }
}

onMounted(refreshDocs)
</script>

<template>
  <div class="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
    <!-- 标题 -->
    <div class="p-4 border-b border-gray-800">
      <h1 class="text-lg font-bold text-white flex items-center gap-2">
        🔍 代码分析助手
      </h1>
    </div>

    <!-- 新建会话 -->
    <div class="p-3">
      <button
        class="w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white text-sm
               rounded-lg transition-colors"
        @click="emit('newSession')"
      >
        + 新建会话
      </button>
    </div>

    <!-- 会话列表 -->
    <div class="flex-1 overflow-y-auto px-3">
      <div class="text-xs text-gray-500 mb-2 px-1">会话列表</div>
      <div
        v-for="s in sessions"
        :key="s.id"
        class="px-3 py-2 rounded-lg mb-1 text-sm cursor-pointer truncate transition-colors"
        :class="s.id === currentSession
          ? 'bg-gray-700 text-white'
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'"
        @click="emit('selectSession', s.id)"
      >
        {{ s.title || s.id }}
      </div>
    </div>

    <!-- 知识库管理 -->
    <div class="border-t border-gray-800 p-3">
      <button
        class="w-full py-2 px-3 text-sm text-gray-400 hover:text-white
               hover:bg-gray-800 rounded-lg transition-colors text-left
               flex items-center justify-between"
        @click="toggleDocs"
      >
        <span>📚 知识库 ({{ documents.length }})</span>
        <svg
          class="w-4 h-4 transition-transform duration-300"
          :class="showDocs ? 'rotate-0' : 'rotate-180'"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <div
        v-if="showDocs"
        ref="docsPanel"
        class="overflow-hidden transition-all duration-300 ease-in-out"
        :style="{ maxHeight: panelHeight + 'px' }"
      >
        <div class="mt-2 space-y-2">
          <div
            v-for="doc in documents"
            :key="doc.filename"
            class="text-xs text-gray-500 px-2 py-1 bg-gray-800 rounded truncate"
          >
            {{ doc.filename }}
          </div>
          <FileUpload @uploaded="refreshDocs" />
        </div>
      </div>
    </div>
  </div>
</template>
