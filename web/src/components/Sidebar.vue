<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getDocuments, deleteDocument } from '../api.js'
import FileUpload from './FileUpload.vue'

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  currentSession: { type: String, default: '' },
  collapsed: { type: Boolean, default: false },
})
const emit = defineEmits(['selectSession', 'newSession', 'toggleCollapse', 'deleteSession'])

const pendingDeleteId = ref(null)
const pendingDeleteDoc = ref(null)

function confirmDelete(id) {
  pendingDeleteId.value = id
}

function cancelDelete() {
  pendingDeleteId.value = null
  pendingDeleteDoc.value = null
}

function doDelete() {
  if (pendingDeleteId.value) {
    emit('deleteSession', pendingDeleteId.value)
    pendingDeleteId.value = null
  }
}

function confirmDeleteDoc(filename) {
  pendingDeleteDoc.value = filename
}

async function doDeleteDoc() {
  if (pendingDeleteDoc.value) {
    try {
      await deleteDocument(pendingDeleteDoc.value)
      await refreshDocs()
    } catch {}
    pendingDeleteDoc.value = null
  }
}

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
  <div
    class="bg-gray-900 border-r border-gray-800 flex flex-col h-full
           transition-all duration-300 ease-in-out overflow-hidden"
    :class="collapsed ? 'w-0 border-r-0' : 'w-64'"
  >
    <!-- 标题 -->
    <div class="p-4 border-b border-gray-800 flex items-center justify-between min-w-[256px]">
      <h1 class="text-lg font-bold text-white flex items-center gap-2">
        <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
        </svg>
        CodeLens
      </h1>
      <button
        class="w-7 h-7 flex items-center justify-center rounded-md
               text-gray-500 hover:text-white hover:bg-gray-800
               transition-colors cursor-pointer"
        @click="emit('toggleCollapse')"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>
    </div>

    <!-- 新建会话 -->
    <div class="p-3">
      <button
        class="w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white text-sm
               rounded-lg transition-colors cursor-pointer"
        @click="emit('newSession')"
      >
        + 新建会话
      </button>
    </div>

    <!-- 会话列表 -->
    <div class="flex-1 overflow-y-auto px-3">
      <div class="text-xs text-gray-500 mb-2 px-1">会话列表</div>

      <!-- 空状态 -->
      <div v-if="!sessions.length" class="text-center py-8">
        <div class="text-gray-600 text-sm">暂无会话</div>
        <div class="text-gray-700 text-xs mt-1">发送消息自动创建</div>
      </div>

      <TransitionGroup name="session-item">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="group flex items-center px-3 py-2 rounded-lg mb-1 text-sm cursor-pointer
                 transition-colors"
          :class="s.id === currentSession
            ? 'bg-gray-700 text-white'
            : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'"
          @click="emit('selectSession', s.id)"
        >
        <span class="truncate flex-1">{{ s.title || s.id }}</span>
        <button
          class="w-5 h-5 shrink-0 flex items-center justify-center rounded
                 text-gray-600 hover:text-red-400 hover:bg-gray-700
                 opacity-0 group-hover:opacity-100 transition-all cursor-pointer ml-1"
          title="删除会话"
          @click.stop="confirmDelete(s.id)"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
          </svg>
        </button>
      </div>
      </TransitionGroup>
    </div>

    <!-- 知识库管理 -->
    <div class="border-t border-gray-800 p-3">
      <button
        class="w-full py-2 px-3 text-sm text-gray-400 hover:text-white
               hover:bg-gray-800 rounded-lg transition-colors text-left
               flex items-center justify-between"
        @click="toggleDocs"
      >
        <span>
          <svg class="w-4 h-4 inline mr-1.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
          </svg>
          知识库 ({{ documents.length }})
        </span>
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
            class="group flex items-center text-xs text-gray-500 px-2 py-1.5 bg-gray-800 rounded"
          >
            <span class="truncate flex-1">{{ doc.filename }}</span>
            <button
              class="w-4 h-4 shrink-0 flex items-center justify-center rounded
                     text-gray-600 hover:text-red-400
                     opacity-0 group-hover:opacity-100 transition-all cursor-pointer ml-1"
              title="删除文档"
              @click="confirmDeleteDoc(doc.filename)"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <FileUpload @uploaded="refreshDocs" />
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗（会话） -->
    <Teleport to="body">
      <div
        v-if="pendingDeleteId"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="cancelDelete"
      >
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 w-72 shadow-2xl">
          <div class="text-sm text-gray-200 mb-4">确定删除这个会话吗？删除后无法恢复。</div>
          <div class="flex gap-3 justify-end">
            <button
              class="px-4 py-1.5 text-sm text-gray-400 hover:text-white
                     bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors cursor-pointer"
              @click="cancelDelete"
            >
              取消
            </button>
            <button
              class="px-4 py-1.5 text-sm text-white bg-red-600 hover:bg-red-700
                     rounded-lg transition-colors cursor-pointer"
              @click="doDelete"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认弹窗（文档） -->
    <Teleport to="body">
      <div
        v-if="pendingDeleteDoc"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="cancelDelete"
      >
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 w-80 shadow-2xl">
          <div class="text-sm text-gray-200 mb-1">确定删除以下文档吗？</div>
          <div class="text-xs text-gray-400 mb-4 truncate">{{ pendingDeleteDoc }}</div>
          <div class="text-xs text-gray-500 mb-4">文档将从向量库中移除，删除后无法恢复。</div>
          <div class="flex gap-3 justify-end">
            <button
              class="px-4 py-1.5 text-sm text-gray-400 hover:text-white
                     bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors cursor-pointer"
              @click="cancelDelete"
            >
              取消
            </button>
            <button
              class="px-4 py-1.5 text-sm text-white bg-red-600 hover:bg-red-700
                     rounded-lg transition-colors cursor-pointer"
              @click="doDeleteDoc"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
