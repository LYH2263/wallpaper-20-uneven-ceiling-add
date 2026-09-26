<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const wall = ref(null)
const rec = ref(null)
onMounted(async () => {
  wall.value = await getJSON(`/api/walls/${props.id}`)
  try { rec.value = await getJSON(`/api/estimate/uneven-ceiling-recommendation?wall_id=${props.id}`) }
  catch { rec.value = null }
})
</script>
<template>
  <div class="page" v-if="wall"><h1>{{ wall.name }}</h1>
  <p v-if="wall.data_quality==='dirty'" class="warn">{{ wall.note }}</p>
  <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>
  <div v-if="rec" class="rec-box">
    <p v-if="!rec.checked?.length" class="hint">脏数据墙面，暂不评估不齐顶加长。</p>
    <p v-else-if="rec.recommended" class="ok">建议启用不齐顶加长（+{{ rec.extra_cm }}cm）：现有各款卷材不增卷。</p>
    <p v-else class="warn">不建议启用不齐顶加长（+{{ rec.extra_cm }}cm）：部分卷材会增加卷数。</p>
    <table v-if="rec.checked?.length">
      <tr v-for="c in rec.checked" :key="c.roll_id">
        <td>{{ c.roll_name }}</td><td>原 {{ c.rolls_without }} 卷</td><td>加长后 {{ c.rolls_with }} 卷</td>
      </tr>
    </table>
  </div>
  </div>
</template>
