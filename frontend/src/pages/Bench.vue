<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const out = ref(null)
const extendOn = ref(false); const extraCm = ref(10); const err = ref('')
const selWall = computed(() => walls.value.find(w => w.id === wallId.value))
const stale = computed(() => !!out.value && out.value.extend_enabled !== extendOn.value)
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  const st = await getJSON('/api/settings')
  extraCm.value = Number(st.default_extend_cm) || 10
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
async function run(save) {
  err.value = ''
  try {
    const q = `wall_id=${wallId.value}&roll_id=${rollId.value}`
      + (extendOn.value ? `&extend_enabled=true&extra_cm=${Number(extraCm.value)}` : '')
    const body = { wall_id: wallId.value, roll_id: rollId.value, save: !!save, extend_enabled: extendOn.value }
    if (extendOn.value) body.extra_cm = Number(extraCm.value)
    out.value = save ? await postJSON('/api/estimate', body) : await getJSON(`/api/estimate?${q}`)
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label><input type="checkbox" v-model="extendOn"> 不齐顶加长</label>
  <label v-if="extendOn">加长 <input v-model.number="extraCm" type="number" min="0" step="1"> cm</label>
  <p v-if="selWall?.uneven_ceiling" class="hint">该墙面建议启用不齐顶加长（需手动勾选）</p>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <p v-if="out && stale" class="hint">设置已变更，请重新试算</p>
  <div v-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m
  <span v-if="out.extend_enabled" class="hint">（基础 {{ out.base_drop_len_m }}m，+{{ out.extra_cm }}cm）</span>
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>
