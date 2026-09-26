<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template>
  <div class="page"><h1>记录</h1><ul>
    <li v-for="r in items" :key="r.id">
      {{ r.wall_name }} → {{ r.result?.rolls }} 卷 · 每条 {{ r.result?.drop_len_m }}m
      <span v-if="r.result?.uneven_ceiling" class="uc-hint">（不齐顶 +{{ r.result?.extra_cm }}cm，写入时钉住）</span>
    </li>
  </ul></div>
</template>
