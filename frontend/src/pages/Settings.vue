<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const cm = ref(10); const saved = ref(''); const err = ref('')
onMounted(async () => {
  const s = await getJSON('/api/settings')
  cm.value = Number(s.default_extend_cm) || 10
})
async function save() {
  saved.value = ''; err.value = ''
  try {
    const s = await putJSON('/api/settings', { default_extend_cm: Number(cm.value) })
    cm.value = Number(s.default_extend_cm) || cm.value
    saved.value = '已保存'
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>设置</h1>
<label>不齐顶加长默认厘米 <input v-model.number="cm" type="number" min="0" step="1"></label>
<button @click="save">保存</button> <span class="hint">{{ saved }}</span>
<p v-if="err" class="warn">{{ err }}</p></div></template>
