<script setup>
import { ref, reactive, nextTick, watch, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatMessage from './components/ChatMessage.vue'
import { streamChat, uploadFile, getSessions, getSessionMessages, deleteSession } from './api.js'

// 会话管理
const sessions = ref([])
const currentSessionId = ref('')
const currentSession = ref({ id: '', title: '', messages: [] })

// 启动时从后端加载会话列表
onMounted(async () => {
  try {
    const data = await getSessions()
    if (data.sessions?.length) {
      sessions.value = data.sessions.map((s) => ({ ...s, messages: [] }))
      await selectSession(sessions.value[0].id)
    }
  } catch {}
})

function newSession() {
  const id = `session_${Date.now()}`
  const s = { id, title: `新会话`, messages: [] }
  sessions.value.unshift(s)
  currentSessionId.value = id
  currentSession.value = s
}

async function selectSession(id) {
  currentSessionId.value = id
  let s = sessions.value.find((s) => s.id === id)
  if (!s) return

  if (!s.messages.length) {
    try {
      const data = await getSessionMessages(id)
      s.messages = data.messages || []
    } catch {}
  }
  currentSession.value = s
  scrollToBottom()
}

async function removeSession(id) {
  try {
    await deleteSession(id)
  } catch {}
  sessions.value = sessions.value.filter((s) => s.id !== id)
  if (currentSessionId.value === id) {
    if (sessions.value.length) {
      await selectSession(sessions.value[0].id)
    } else {
      // 全部删完，清空状态，显示空界面
      currentSessionId.value = ''
      currentSession.value = { id: '', title: '', messages: [] }
    }
  }
}

// 对话
const inputText = ref('')
const isStreaming = ref(false)
const chatContainer = ref(null)
const sidebarCollapsed = ref(false)

function scrollToBottom(force = false) {
  nextTick(() => {
    const el = chatContainer.value
    if (!el) return
    // 只在用户已经在底部附近（100px 内）或强制时才自动滚动
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100
    if (force || isNearBottom) {
      el.scrollTop = el.scrollHeight
    }
  })
}

async function sendMessage() {
  const query = inputText.value.trim()
  if (!query || isStreaming.value) return

  // 无会话时自动创建
  if (!sessions.value.length || !currentSession.value.id) {
    newSession()
  }

  const msgs = currentSession.value.messages
  msgs.push({ role: 'user', content: query })
  inputText.value = ''
  scrollToBottom(true)

  const aiMsg = reactive({ role: 'assistant', content: '', loading: true })
  msgs.push(aiMsg)
  isStreaming.value = true
  scrollToBottom(true)

  // 自动命名：用第一条消息的前 20 字作为标题
  if (msgs.length <= 2) {
    currentSession.value.title = query.slice(0, 20) + (query.length > 20 ? '...' : '')
  }

  await streamChat(
    query,
    currentSessionId.value,
    (token) => {
      aiMsg.content += token
      aiMsg.loading = false
      scrollToBottom()
    },
    () => {
      aiMsg.loading = false
      isStreaming.value = false
      scrollToBottom()
    }
  )
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 文件上传
const fileInput = ref(null)
const isDragging = ref(false)
const uploadStatus = ref('') // '', 'uploading', 'success', 'error'
const uploadMessage = ref('')
let dragCounter = 0
let statusTimer = null

function clearStatus() {
  if (statusTimer) clearTimeout(statusTimer)
  statusTimer = setTimeout(() => {
    uploadStatus.value = ''
    uploadMessage.value = ''
  }, 3000)
}

async function handleUploadFiles(files) {
  if (!files?.length) return
  uploadStatus.value = 'uploading'
  uploadMessage.value = '上传中...'

  for (const file of files) {
    try {
      const result = await uploadFile(file)
      uploadStatus.value = 'success'
      uploadMessage.value = `✅ ${result.message}`
    } catch (err) {
      uploadStatus.value = 'error'
      uploadMessage.value = `❌ ${err.message}`
    }
  }
  clearStatus()
}

function onFileInputChange(e) {
  handleUploadFiles(e.target.files)
  e.target.value = ''
}

function onInputAreaDragEnter(e) {
  e.preventDefault()
  dragCounter++
  isDragging.value = true
}

function onInputAreaDragLeave(e) {
  e.preventDefault()
  dragCounter--
  if (dragCounter <= 0) {
    dragCounter = 0
    isDragging.value = false
  }
}

function onInputAreaDrop(e) {
  e.preventDefault()
  dragCounter = 0
  isDragging.value = false
  handleUploadFiles(e.dataTransfer?.files)
}
</script>

<template>
  <div class="h-screen flex bg-gray-950 text-gray-200">
    <!-- 侧边栏 -->
    <Sidebar
      :sessions="sessions"
      :currentSession="currentSessionId"
      :collapsed="sidebarCollapsed"
      @selectSession="selectSession"
      @newSession="newSession"
      @toggleCollapse="sidebarCollapsed = !sidebarCollapsed"
      @deleteSession="removeSession"
    />

    <!-- 收起时的展开按钮 -->
    <button
      v-if="sidebarCollapsed"
      class="absolute top-4 left-4 z-20 w-8 h-8 flex items-center justify-center
             rounded-lg bg-gray-800 border border-gray-700 text-gray-400
             hover:text-white hover:bg-gray-700 transition-colors cursor-pointer"
      @click="sidebarCollapsed = false"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
      </svg>
    </button>

    <!-- 主区域 -->
    <div class="flex-1 flex flex-col">
      <!-- 对话区域 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto">
        <!-- 空状态 -->
        <div
          v-if="!currentSession.messages.length"
          class="h-full flex flex-col items-center justify-center text-gray-500"
        >
          <div class="w-16 h-16 mb-4 rounded-2xl bg-emerald-600/10 border border-emerald-600/20
                      flex items-center justify-center">
            <svg class="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
            </svg>
          </div>
          <div class="text-lg font-medium mb-2 text-gray-300">CodeLens</div>
          <div class="text-sm max-w-md text-center leading-relaxed">
            粘贴代码让我帮你审查，或上传文档构建知识库。<br />
            支持代码审查、安全分析、性能诊断、重构建议。
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="py-4">
          <ChatMessage
            v-for="(msg, i) in currentSession.messages"
            :key="i"
            :role="msg.role"
            :content="msg.content"
            :loading="msg.loading"
          />
        </div>
      </div>

      <!-- 输入区域 -->
      <div
        class="border-t border-gray-800 p-4 relative"
        @dragenter="onInputAreaDragEnter"
        @dragover.prevent
        @dragleave="onInputAreaDragLeave"
        @drop="onInputAreaDrop"
      >
        <!-- 拖拽遮罩 -->
        <div
          v-if="isDragging"
          class="absolute inset-0 z-10 bg-blue-600/10 border-2 border-dashed
                 border-blue-500 rounded-xl flex items-center justify-center
                 pointer-events-none"
        >
          <span class="text-blue-400 text-sm font-medium">
            松开鼠标上传文件
          </span>
        </div>

        <!-- 上传状态提示 -->
        <div
          v-if="uploadMessage"
          class="max-w-4xl mx-auto mb-2 text-xs px-2"
          :class="uploadStatus === 'error' ? 'text-red-400' : 'text-green-400'"
        >
          {{ uploadMessage }}
        </div>

        <div class="max-w-4xl mx-auto flex gap-2 items-center">
          <!-- 上传按钮图标 -->
          <input
            ref="fileInput"
            type="file"
            accept=".md,.txt,.pdf,.docx,.py,.js,.ts,.jsx,.tsx,.java,.go,.rs,.c,.cpp,.h,.cs,.rb,.php,.sql,.sh,.yaml,.yml,.json,.xml,.html,.css,.vue"
            multiple
            class="hidden"
            @change="onFileInputChange"
          />
          <button
            class="w-9 h-9 shrink-0 flex items-center justify-center rounded-lg
                   text-gray-400 hover:text-white hover:bg-gray-800
                   transition-colors relative group"
            title="上传文档（支持 .md / .txt / .pdf / .docx）"
            @click="fileInput?.click()"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
            </svg>
            <!-- Tooltip -->
            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5
                        bg-gray-800 text-xs text-gray-300 rounded-lg whitespace-nowrap
                        opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none
                        border border-gray-700 shadow-lg">
              支持文档（.md .txt .pdf .docx）和代码文件（.py .js .java .go 等）
            </div>
          </button>

          <!-- 输入框 -->
          <textarea
            v-model="inputText"
            rows="1"
            placeholder="输入代码或问题... (Enter 发送, Shift+Enter 换行)"
            class="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2
                   text-sm text-gray-200 resize-none focus:outline-none
                   focus:border-blue-500 placeholder-gray-500 leading-5
                   min-h-[36px] max-h-[200px]"
            style="field-sizing: content;"
            @keydown="handleKeydown"
          />

          <!-- 发送按钮 -->
          <button
            class="w-9 h-9 shrink-0 flex items-center justify-center rounded-lg
                   bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700
                   disabled:cursor-not-allowed text-white transition-colors"
            :disabled="!inputText.trim() || isStreaming"
            @click="sendMessage"
          >
            <svg v-if="!isStreaming" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
