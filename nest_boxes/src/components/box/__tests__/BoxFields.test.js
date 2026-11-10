import { describe, expect, it, vi } from "vitest"
import { nextTick } from "vue"
import { mount } from "@vue/test-utils"

import BoxFields from "@/components/box/BoxFields.vue"

vi.mock("@/components/map/LocationPicker.vue", () => ({ default: {} }))

const types = [
  { id: 1, name: "sýkorník", hole_shape: "round", hole_min: 27, hole_max: 35 },
]

describe("BoxFields", () => {
  it("settles after an edit when the type follows the hole", async () => {
    const updates = []
    const wrapper = mount(BoxFields, {
      props: {
        types,
        center: { type: "Point", coordinates: [16.6, 49.2] },
        fields: ["name", "hole_shape", "hole_size", "type"],
        modelValue: { name: "", hole_shape: "round", hole_size: 32, type: 1 },
        "onUpdate:modelValue": value => {
          updates.push(value)
          wrapper.setProps({ modelValue: value })
        },
      },
    })
    await wrapper.find("#box-name").setValue("A1")
    for (let tick = 0; tick < 20; tick++) await nextTick()
    expect(updates.length).toBeLessThan(3)
  })
})
