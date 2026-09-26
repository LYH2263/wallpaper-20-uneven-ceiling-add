<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const out = ref(null)
const uneven = ref(false)
const extraCm = ref(10)
const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
  const s = await getJSON('/api/settings')
  extraCm.value = Number(s.uneven_ceiling_extra_cm) || 10
})
function params() {
  const p = { wall_id: wallId.value, roll_id: rollId.value }
  if (uneven.value) { p.uneven_ceiling = true; p.extra_cm = Number(extraCm.value) }
  return p
}
async function run(save) {
  err.value = ''
  try {
    out.value = save
      ? await postJSON('/api/estimate', { ...params(), save: true })
      : await getJSON(`/api/estimate?${new URLSearchParams(params())}`)
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <label class="uc-toggle"><input type="checkbox" v-model="uneven" /> 不齐顶加长</label>
  <input v-if="uneven" v-model.number="extraCm" type="number" min="0.1" step="0.5" class="uc-input" /> cm
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="out"><strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 ·
    每条 <template v-if="out.uneven_ceiling"><s>{{ (out.drop_len_m - out.extra_m).toFixed(3) }}</s> → </template>{{ out.drop_len_m }}m
    <span v-if="out.uneven_ceiling" class="uc-hint">（不齐顶 +{{ out.extra_cm }}cm）</span>
  <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>
