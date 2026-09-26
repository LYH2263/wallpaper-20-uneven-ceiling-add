<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const run = ref(null)
onMounted(async () => { run.value = await getJSON(`/api/runs/${props.id}`) })
</script>
<template>
  <div class="page" v-if="run"><h1>记录 #{{ run.id }}</h1>
  <p>{{ run.wall_name }} → {{ run.roll_name }}</p>
  <p v-if="run.note">{{ run.note }}</p>
  <p>{{ run.created_at }}</p>
  <p><strong>{{ run.result?.rolls }} 卷</strong> · {{ run.result?.drops }} 条 · 每条 {{ run.result?.drop_len_m }}m</p>
  <p v-if="run.result?.extend_enabled">不齐顶加长：启用 +{{ run.result.extra_cm }}cm；基础 {{ run.result.base_drop_len_m }}m</p>
  <p v-else>不齐顶加长：未启用</p>
  <p><router-link to="/history">返回记录</router-link></p></div>
</template>
