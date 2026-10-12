<script setup>
import { EditorContent, useEditor } from "@tiptap/vue-3"
import StarterKit from "@tiptap/starter-kit"
import { NButton, NInput, NInputGroup, NPopover } from "naive-ui"
import {
  faBold,
  faItalic,
  faLink,
  faListOl,
  faListUl,
} from "@fortawesome/free-solid-svg-icons"
import { ref, watch } from "vue"
import { icon } from "@/contrib/composables/render.js"
import { _ } from "@/composables/translations.js"

const value = defineModel("value")

// The backend's sanitizer (api/cookbook/serializers.py) keeps exactly the
// markup these extensions produce, so the two have to change together.
const editor = useEditor({
  content: value.value ?? "",
  extensions: [
    StarterKit.configure({
      blockquote: false,
      code: false,
      codeBlock: false,
      heading: false,
      horizontalRule: false,
      strike: false,
      underline: false,
      link: {
        openOnClick: false,
        defaultProtocol: "https",
        HTMLAttributes: { target: "_blank", rel: "noopener noreferrer" },
      },
    }),
  ],
  onUpdate: ({ editor }) => (value.value = editor.isEmpty ? "" : editor.getHTML()),
})

// Writing the editor's own output back into it would reset the cursor.
watch(value, html => {
  const current = editor.value.isEmpty ? "" : editor.value.getHTML()
  if (html !== current) editor.value.commands.setContent(html ?? "")
})

const formats = [
  { name: "bold", hint: "bold", icon: faBold, toggle: chain => chain.toggleBold() },
  {
    name: "italic",
    hint: "italic",
    icon: faItalic,
    toggle: chain => chain.toggleItalic(),
  },
  {
    name: "bulletList",
    hint: "bullet_list",
    icon: faListUl,
    toggle: chain => chain.toggleBulletList(),
  },
  {
    name: "orderedList",
    hint: "ordered_list",
    icon: faListOl,
    toggle: chain => chain.toggleOrderedList(),
  },
]

const linkUrl = ref("")
const showLinkInput = ref(false)
const openLinkInput = () => {
  linkUrl.value = editor.value.getAttributes("link").href ?? ""
  showLinkInput.value = true
}
const insertLink = () => {
  const chain = editor.value.chain().focus().extendMarkRange("link")
  const url = linkUrl.value.trim()
  const href = /^[a-z]+:/i.test(url) ? url : `https://${url}`
  if (url) chain.setLink({ href }).run()
  else chain.unsetLink().run()
  showLinkInput.value = false
}
</script>

<template>
  <div v-if="editor" class="html-editor">
    <div class="toolbar">
      <n-button
        v-for="format in formats"
        :key="format.name"
        size="tiny"
        quaternary
        :type="editor.isActive(format.name) ? 'primary' : 'default'"
        :title="_.editor[format.hint]"
        :aria-label="_.editor[format.hint]"
        :render-icon="icon(format.icon)"
        @click="format.toggle(editor.chain().focus()).run()"
      />
      <n-popover
        v-model:show="showLinkInput"
        trigger="manual"
        placement="bottom-start"
        @clickoutside="showLinkInput = false"
      >
        <template #trigger>
          <n-button
            size="tiny"
            quaternary
            :type="editor.isActive('link') ? 'primary' : 'default'"
            :title="_.editor.link"
            :aria-label="_.editor.link"
            :render-icon="icon(faLink)"
            @click="openLinkInput"
          />
        </template>
        <n-input-group>
          <n-input
            v-model:value="linkUrl"
            size="small"
            placeholder="https://"
            autofocus
            @keydown.enter.prevent="insertLink"
          />
          <n-button size="small" type="primary" @click="insertLink">
            {{ _.editor.insert }}
          </n-button>
        </n-input-group>
      </n-popover>
    </div>
    <EditorContent :editor="editor" class="content html-text" />
  </div>
</template>

<style scoped>
.html-editor {
  width: 100%;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--surface);
}

.html-editor:focus-within {
  border-color: var(--primary);
}

.toolbar {
  display: flex;
  gap: 2px;
  padding: 2px 4px;
  border-bottom: 1px solid var(--line);
  background: var(--surface-muted);
}

.content :deep(.ProseMirror) {
  min-height: 2.2em;
  padding: 4px 10px;
  outline: none;
}
</style>
