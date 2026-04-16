<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../markdown.js'

const props = defineProps({
  role: { type: String, required: true }, // 'user' | 'assistant'
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const html = computed(() => renderMarkdown(props.content))
</script>

<template>
  <div class="flex gap-3 px-4 py-3" :class="role === 'user' ? 'justify-end' : ''">
    <!-- 头像 -->
    <div
      v-if="role === 'assistant'"
      class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white text-sm shrink-0"
    >
      🤖
    </div>

    <!-- 消息体 -->
    <div
      class="max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed"
      :class="
        role === 'user'
          ? 'bg-blue-600 text-white rounded-br-sm'
          : 'bg-gray-800 text-gray-200 rounded-bl-sm'
      "
    >
      <!-- 用户消息纯文本 -->
      <div v-if="role === 'user'" class="whitespace-pre-wrap">{{ content }}</div>

      <!-- AI 消息 Markdown 渲染 -->
      <div v-else>
        <div v-if="loading && !content" class="flex gap-1 py-1">
          <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms" />
          <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms" />
          <span class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms" />
        </div>
        <div v-else class="markdown-body" v-html="html" />
      </div>
    </div>

    <!-- 用户头像 -->
    <div
      v-if="role === 'user'"
      class="w-8 h-8 rounded-lg bg-gray-600 flex items-center justify-center text-white text-sm shrink-0"
    >
      👤
    </div>
  </div>
</template>
