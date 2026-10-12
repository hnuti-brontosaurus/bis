<script setup>
import { EditorContent, useEditor } from "@tiptap/vue-3"
import { BubbleMenu } from "@tiptap/vue-3/menus"
import Image from "@tiptap/extension-image"
import StarterKit from "@tiptap/starter-kit"
import { NButton, NInput, NInputGroup, NPopover } from "naive-ui"
import {
  faBold,
  faImage,
  faItalic,
  faLink,
  faListOl,
  faListUl,
  faMinus,
  faQuoteLeft,
} from "@fortawesome/free-solid-svg-icons"
import { ref, watch } from "vue"
import { toDataUri } from "@/contrib/composables/helpers.js"
import { icon } from "@/contrib/composables/render.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { _ } from "@/composables/translations.js"

const value = defineModel("value")
const props = defineProps({
  // Headings, quotes and horizontal rules.
  rich: { type: Boolean, default: false },
  // Turns on images: takes a data URI, resolves to the uploaded image's URL.
  uploadImage: { type: Function, default: null },
})

// The backend's sanitizer (api/cookbook/serializers.py) keeps exactly the
// markup these extensions produce, so the two have to change together.
// What `rich` and `uploadImage` add is kept only by `ArticleHTMLField`.
// Stored as a class, so the page lays the image out the same way at any
// screen width.
const imageSizes = [
  { size: "small-left", hint: "image_small_left" },
  { size: "small-right", hint: "image_small_right" },
  { size: "medium", hint: "image_medium" },
  { size: "full", hint: "image_full" },
]
const SizedImage = Image.extend({
  addAttributes() {
    return {
      ...this.parent(),
      size: {
        default: "small-left",
        parseHTML: element =>
          imageSizes.find(({ size }) => element.classList.contains(`size-${size}`))
            ?.size,
        renderHTML: ({ size }) => ({ class: `size-${size}` }),
      },
    }
  },
})

const editor = useEditor({
  content: value.value ?? "",
  extensions: [
    StarterKit.configure({
      blockquote: props.rich && {},
      code: false,
      codeBlock: false,
      heading: props.rich && { levels: [2, 3] },
      horizontalRule: props.rich && {},
      strike: false,
      underline: false,
      link: {
        openOnClick: false,
        defaultProtocol: "https",
        HTMLAttributes: { target: "_blank", rel: "noopener noreferrer" },
      },
    }),
    ...(props.uploadImage ? [SizedImage] : []),
  ],
  onUpdate: ({ editor }) => (value.value = editor.isEmpty ? "" : editor.getHTML()),
})

// Writing the editor's own output back into it would reset the cursor.
watch(value, html => {
  const current = editor.value.isEmpty ? "" : editor.value.getHTML()
  if (html !== current) editor.value.commands.setContent(html ?? "")
})

const headingFormats = [2, 3].map(level => ({
  name: "heading",
  attributes: { level },
  hint: `heading_${level}`,
  label: `H${level}`,
  toggle: chain => chain.toggleHeading({ level }),
}))

const richFormats = [
  ...headingFormats,
  {
    name: "blockquote",
    hint: "quote",
    icon: faQuoteLeft,
    toggle: chain => chain.toggleBlockquote(),
  },
  {
    name: "horizontalRule",
    hint: "horizontal_rule",
    icon: faMinus,
    toggle: chain => chain.setHorizontalRule(),
  },
]

const formats = [
  ...(props.rich ? richFormats : []),
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

const imageInput = ref()
const uploadingImage = ref(false)
const insertImage = async event => {
  const [file] = event.target.files
  event.target.value = ""
  uploadingImage.value = true
  try {
    const src = await props.uploadImage(await toDataUri(file))
    editor.value.chain().focus().setImage({ src }).run()
  } catch (e) {
    handleAxiosError(_.value.editor.image_error)(e)
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
        v-for="format in formats"
        :key="format.hint"
        size="tiny"
        quaternary
        :type="editor.isActive(format.name, format.attributes) ? 'primary' : 'default'"
        :title="_.editor[format.hint]"
        :aria-label="_.editor[format.hint]"
        :render-icon="format.icon && icon(format.icon)"
        @click="format.toggle(editor.chain().focus()).run()"
        >{{ format.label }}</n-button
      >
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
      <template v-if="uploadImage">
        <n-button
          size="tiny"
          quaternary
          :loading="uploadingImage"
          :title="_.editor.image"
          :aria-label="_.editor.image"
          :render-icon="icon(faImage)"
          @click="imageInput.click()"
        />
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          hidden
          @change="insertImage"
        />
      </template>
    </div>
    <BubbleMenu
      v-if="uploadImage"
      :editor="editor"
      plugin-key="imageSize"
      :should-show="({ editor }) => editor.isActive('image')"
    >
      <div class="image-menu">
        <n-button
          v-for="option in imageSizes"
          :key="option.hint"
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
          >{{ _.editor[option.hint] }}</n-button
        >
      </div>
    </BubbleMenu>
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

.image-menu {
  display: flex;
  gap: 2px;
  padding: 2px 4px;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--surface);
  box-shadow: 0 2px 8px rgb(0 0 0 / 15%);
}

.content :deep(.ProseMirror-selectednode) {
  outline: 2px solid var(--primary);
}

.content :deep(.ProseMirror) {
  min-height: 2.2em;
  padding: 4px 10px;
  outline: none;
}
</style>
