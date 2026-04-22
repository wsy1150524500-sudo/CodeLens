<script setup>
import { computed, ref, onMounted } from 'vue'
import { renderMarkdown } from '../markdown.js'

const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const html = computed(() => renderMarkdown(props.content))
const visible = ref(false)
onMounted(() => { requestAnimationFrame(() => { visible.value = true }) })
</script>

<template>
  <div
    class="flex gap-3 px-12 py-4 transition-all duration-300 ease-out"
    :class="[
      role === 'user' ? 'justify-end' : '',
      visible
        ? 'opacity-100 translate-x-0'
        : role === 'user'
          ? 'opacity-0 translate-x-8'
          : 'opacity-0 -translate-x-8'
    ]"
  >
    <!-- AI 头像 -->
    <div
      v-if="role === 'assistant'"
      class="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-600/30
             flex items-center justify-center shrink-0"
    >
      <svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
      </svg>
    </div>

    <!-- 消息体 -->
    <div
      class="max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed"
      :class="
        role === 'user'
          ? 'bg-blue-600/90 text-white rounded-br-sm'
          : 'bg-gray-800/80 text-gray-200 rounded-bl-sm border border-gray-700/50'
      "
    >
      <!-- 用户消息 -->
      <div v-if="role === 'user'" class="whitespace-pre-wrap">{{ content }}</div>

      <!-- AI 消息 -->
      <div v-else>
        <!-- 加载骨架 -->
        <div v-if="loading && !content" class="flex flex-col gap-2 py-1">
          <div class="h-3 w-48 bg-gray-700 rounded animate-pulse" />
          <div class="h-3 w-36 bg-gray-700 rounded animate-pulse" />
          <div class="h-3 w-24 bg-gray-700 rounded animate-pulse" />
        </div>
        <!-- 内容 + 流式光标 -->
        <div v-else class="markdown-body">
          <span v-html="html" />
          <span
            v-if="loading"
            class="inline-block w-2 h-4 bg-emerald-400 ml-0.5 animate-pulse rounded-sm align-text-bottom"
          />
        </div>
      </div>
    </div>

    <!-- 用户头像 -->
    <div
      v-if="role === 'user'"
      class="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-600/30
             flex items-center justify-center shrink-0"
    >
      <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0" />
      </svg>
    </div>
  </div>
</template>
