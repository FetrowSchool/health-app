// TEST ENTRY ONLY. Production Vite inputs never reference this file.
import { createApp } from 'vue'
import App from '../../src/App.vue'
import '../../src/style.css'
const tracks=[]
const showTracks=()=>{document.documentElement.dataset.mockMicrophoneStopped=String(tracks.every(t=>t.stopped))}
class Track extends EventTarget {
 kind='audio';enabled=true;stopped=false
 stop(){this.stopped=true;showTracks()}
}
Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async options=>{
 if(options.video!==false||options.audio!==true)throw Error('Unexpected constraints')
 const track=new Track();tracks.push(track);showTracks()
 return{getTracks:()=>[track],getAudioTracks:()=>[track]}
}}})
const emit=(target,type,fields={})=>target.dispatchEvent(Object.assign(new Event(type),fields))
class Channel extends EventTarget {
 readyState='open'
 send(value){if(JSON.parse(value).type==='session.close')setTimeout(()=>this.message({type:'session.closed'}),10)}
 close(){this.readyState='closed';emit(this,'close')}
 message(data){emit(this,'message',{data:JSON.stringify(data)})}
}
class Peer extends EventTarget {
 iceGatheringState='complete';connectionState='new';channel=null
 addTrack(){}
 createDataChannel(name){if(name!=='oai-events')throw Error('Unexpected channel');this.channel=new Channel();return this.channel}
 async createOffer(){return{type:'offer',sdp:'v=0\r\nevaluation-offer'}}
 async setLocalDescription(value){this.localDescription=value}
 async setRemoteDescription(){setTimeout(()=>{
  if(this.connectionState==='closed')return
  this.connectionState='connected';emit(this,'connectionstatechange')
  this.channel.message({type:'session.started',session:{id:'evaluation-session'}})
  const events=[
   ['input','Fictional example: I keep putting off a school assignment.',0,500],
   ['output','Choose one small task and give it five minutes.',600,1500],
   ['input','Which Pause exercise could I try?',1600,2000],
   ['output','You can choose Paced Breathing from Home, or we can keep talking.',2100,3500],
   ['input','Actually, no exercise. Let us keep talking.',2500,3000],
   ['output','We can keep talking about one practical next step.',3600,4500],
  ]
  for(const [speaker,delta,start_ms,end_ms] of events)this.channel.message({type:`session.${speaker}_transcript.delta`,delta,start_ms,end_ms})
 },20)}
 close(){this.connectionState='closed';emit(this,'connectionstatechange')}
}
window.RTCPeerConnection=Peer
showTracks()
const style=document.createElement('style');style.textContent='body{padding-top:36px}#evaluation-banner{position:fixed;top:0;left:0;right:0;z-index:99;background:#dbe6ec;color:#253641;text-align:center;font:12px/18px sans-serif;padding:0 6px;min-height:36px}.app-header{top:36px}';document.head.append(style)
createApp(App).mount('#app')
