<template>
  <q-btn round dense flat icon="apps" color="white">
    <q-menu anchor="bottom right" self="top right">
      <q-card class="bg-card text-primary" style="min-width:280px;max-width:320px">
        <q-card-section class="row q-col-gutter-md q-pa-md">
          <q-item
            v-for="app in apps"
            :key="app.name"
            clickable
            tag="a"
            :href="app.url"
            target="_blank"
            class="col-4 column items-center text-center app-tile"
          >
            <img :src="app.icon" style="height:48px" />
            <div class="text-caption q-mt-sm">{{ app.name }}</div>
          </q-item>
        </q-card-section>
      </q-card>
    </q-menu>
  </q-btn>
</template>

<script setup>
import upseal from 'assets/upseal.png'
import upcebulogo from 'assets/upcebulogo.png'

const apps = [
  { name: 'AMIS', url: 'http://amis.upcebu.edu.ph', icon: upseal },
  { name: 'BULSA', url: 'http://bulsa.up.edu.ph', icon: upseal },
  { name: 'PUSO', url: 'http://puso.up.edu.ph', icon: upseal },
  { name: 'CORE', url: 'http://core.upcebu.edu.ph', icon: upcebulogo },
  { name: 'KAT-ON', url: 'http://lms.upcebu.edu.ph', icon: upcebulogo },
  { name: 'VMS', url: 'http://vms.upcebu.edu.ph', icon: upcebulogo },
]
</script>
