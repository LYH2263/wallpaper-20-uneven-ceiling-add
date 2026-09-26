<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const defaultExtra = ref(10)
const msg = ref(''); const err = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  defaultExtra.value = Number(s.value.uneven_ceiling_extra_cm) || 10
})
async function saveDefault() {
  msg.value = ''; err.value = ''
  try {
    const r = await putJSON('/api/settings/uneven-ceiling-extra-cm', { extra_cm: Number(defaultExtra.value) })
    defaultExtra.value = r.uneven_ceiling_extra_cm
    msg.value = '已保存默认加长'
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>设置</h1>
  <div class="setting-row">
    <label>不齐顶默认加长</label>
    <input v-model.number="defaultExtra" type="number" min="0.1" step="0.5" /> cm
    <button @click="saveDefault">保存默认</button>
    <span v-if="msg" class="ok">{{ msg }}</span>
    <span v-if="err" class="warn">{{ err }}</span>
    <p class="hint">测算台启用不齐顶加长但未单独填加长厘米时，按此默认值计算；仅影响之后的测算，不改写历史记录。</p>
  </div>
</div></template>
