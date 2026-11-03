<script setup>
import { ref, watch } from "vue"
import { EditorContent, useEditor } from "@tiptap/vue-3"
import { BubbleMenu } from "@tiptap/vue-3/menus"
import Image from "@tiptap/extension-image"
import StarterKit from "@tiptap/starter-kit"
import { NButton, NInput, NInputGroup, NPopover } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { fileDataUri } from "@/composables/files.js"
import { reportError } from "@/data/errors.js"

const value = defineModel("value", { type: String, default: "" })
const props = defineProps({
  // Takes a data URI, resolves to the uploaded image's URL
  uploadImage: { type: Function, required: true },
})

// The backend keeps exactly the markup these extensions produce
// (ArticleHTMLField in api/cookbook/serializers.py, shared with the cookbook's
// articles), so the two have to change together.
const IMAGE_SIZES = [
  { size: "small-left", label: "Malý vlevo" },
  { size: "small-right", label: "Malý vpravo" },
  { size: "medium", label: "Střední" },
  { size: "full", label: "Celá šířka" },
]

const SizedImage = Image.extend({
  addAttributes() {
    return {
      ...this.parent(),
      size: {
        default: "small-left",
        parseHTML: element =>
          IMAGE_SIZES.find(({ size }) => element.classList.contains(`size-${size}`))
            ?.size,
        renderHTML: ({ size }) => ({ class: `size-${size}` }),
      },
    }
  },
})

const editor = useEditor({
  content: value.value,
  extensions: [
    StarterKit.configure({
      code: false,
      codeBlock: false,
      heading: { levels: [2, 3] },
      strike: false,
      underline: false,
      link: {
        openOnClick: false,
        defaultProtocol: "https",
        HTMLAttributes: { target: "_blank", rel: "noopener noreferrer" },
      },
    }),
    SizedImage,
  ],
  onUpdate: ({ editor }) => (value.value = editor.isEmpty ? "" : editor.getHTML()),
})

// Writing the editor's own output back into it would reset the cursor.
watch(value, html => {
  const current = editor.value.isEmpty ? "" : editor.value.getHTML()
  if (html !== current) editor.value.commands.setContent(html)
})

const FORMATS = [
  {
    name: "heading",
    attributes: { level: 2 },
    label: "H2",
    title: "Nadpis",
    toggle: chain => chain.toggleHeading({ level: 2 }),
  },
  {
    name: "heading",
    attributes: { level: 3 },
    label: "H3",
    title: "Podnadpis",
    toggle: chain => chain.toggleHeading({ level: 3 }),
  },
  { name: "bold", label: "B", title: "Tučně", toggle: chain => chain.toggleBold() },
  {
    name: "italic",
    label: "I",
    title: "Kurzíva",
    toggle: chain => chain.toggleItalic(),
  },
  {
    name: "bulletList",
    label: "•",
    title: "Odrážky",
    toggle: chain => chain.toggleBulletList(),
  },
  {
    name: "orderedList",
    label: "1.",
    title: "Číslovaný seznam",
    toggle: chain => chain.toggleOrderedList(),
  },
  {
    name: "blockquote",
    label: "„“",
    title: "Zvýraznění",
    toggle: chain => chain.toggleBlockquote(),
  },
  {
    name: "horizontalRule",
    label: "—",
    title: "Oddělovač",
    toggle: chain => chain.setHorizontalRule(),
  },
]

const imageInput = ref(null)
const uploadingImage = ref(false)
const insertImage = async event => {
  const [file] = event.target.files
  event.target.value = ""
  uploadingImage.value = true
  try {
    const src = await props.uploadImage(await fileDataUri(file))
    editor.value.chain().focus().setImage({ src }).run()
  } catch (error) {
    reportError(error)
  } finally {
    uploadingImage.value = false
  }
}

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
        v-for="format in FORMATS"
        :key="format.title"
        size="small"
        quaternary
        :type="editor.isActive(format.name, format.attributes) ? 'primary' : 'default'"
        :title="format.title"
        :aria-label="format.title"
        @click="format.toggle(editor.chain().focus()).run()"
      >
        {{ format.label }}
      </n-button>
      <n-popover
        v-model:show="showLinkInput"
        trigger="manual"
        placement="bottom-start"
        @clickoutside="showLinkInput = false"
      >
        <template #trigger>
          <n-button
            size="small"
            quaternary
            :type="editor.isActive('link') ? 'primary' : 'default'"
            title="Odkaz"
            aria-label="Odkaz"
            @click="openLinkInput"
          >
            <AppIcon name="link" />
          </n-button>
        </template>
        <n-input-group>
          <n-input
            v-model:value="linkUrl"
            size="small"
            placeholder="https://"
            autofocus
            @keydown.enter.prevent="insertLink"
          />
          <n-button size="small" type="primary" @click="insertLink">Vložit</n-button>
        </n-input-group>
      </n-popover>
      <n-button
        size="small"
        quaternary
        :loading="uploadingImage"
        title="Obrázek"
        aria-label="Obrázek"
        @click="imageInput.click()"
      >
        <AppIcon name="camera" />
      </n-button>
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        hidden
        @change="insertImage"
      />
    </div>
    <BubbleMenu
      :editor="editor"
      plugin-key="imageSize"
      :should-show="({ editor }) => editor.isActive('image')"
    >
      <div class="image-menu">
        <n-button
          v-for="option in IMAGE_SIZES"
          :key="option.size"
          size="tiny"
          quaternary
          :type="
            editor.isActive('image', { size: option.size }) ? 'primary' : 'default'
          "
          @click="
            editor
              .chain()
              .focus()
              .updateAttributes('image', { size: option.size })
              .run()
          "
        >
          {{ option.label }}
        </n-button>
      </div>
    </BubbleMenu>
    <EditorContent :editor="editor" class="content html-text" />
  </div>
</template>

<style scoped>
.html-editor {
  border: 1px solid var(--line-strong);
  border-radius: var(--r-in);
  background: var(--surface);
  overflow: hidden;
}

.html-editor:focus-within {
  border-color: var(--primary);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 4px 6px;
  border-bottom: 1px solid var(--line);
  background: var(--surface-2);
}

.toolbar .icon {
  width: 17px;
  height: 17px;
}

.image-menu {
  display: flex;
  gap: 2px;
  padding: 3px 4px;
  border: 1px solid var(--line);
  border-radius: var(--r-in);
  background: var(--surface);
  box-shadow: 0 2px 8px var(--shadow-c);
}

.content :deep(.ProseMirror) {
  min-height: 240px;
  padding: 12px 16px;
  outline: none;
}

.content :deep(.ProseMirror-selectednode) {
  outline: 2px solid var(--primary);
}
</style>
