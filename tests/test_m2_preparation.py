"""Light local control-flow tests with mocks. Never network/OVS acceptance."""
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
import shlex
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'automation'))
import m2_run_queue as queue
import m2_console_job as transport
import m2_mirror_guest_prepared as guest
from validate_m3_plan import validate
import m4_benign_frame as marker
from m2_tap_frame_test import verify_qemu_mapping


class Preparation(unittest.TestCase):
    def baseline(self):
        data=json.loads((ROOT/'docs/evidence/M2/isolated-bridge-20261101/guest/after.json').read_text())
        data.setdefault('routes4',[]);data.setdefault('routes6',[])
        return data

    def mirrored(self):
        s=self.baseline()
        s['ports'].append({'_uuid':'mock-capture','name':'ens10','vlan_mode':'trunk','tag':[],'trunks':guest.VLAN})
        s['interfaces'].append({'name':'ens10','ofport':123,'error':[]})
        s['mirrors']=[{'name':'span-suricata','select_all':False,
                       'select_src_port':[p['_uuid'] for p in s['ports'] if p['name'] in guest.DATA],
                       'select_dst_port':[],'select_vlan':guest.VLAN,'output_port':'mock-capture'}]
        return s

    def test_guest_rejects_wrong_tag_and_mirror_destination(self):
        s=self.baseline();guest.check(s)
        next(p for p in s['ports'] if p['name']=='ens3')['tag']=40
        with self.assertRaises(AssertionError):guest.check(s)
        s=self.mirrored();guest.check(s,True)
        s['mirrors'][0]['output_port']='wrong-port'
        with self.assertRaises(AssertionError):guest.check(s,True)

    def test_mirror_failure_attempts_rollback_and_retains_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);(work/'backup-metadata.json').write_text('{}')
            (work/'before.json').write_text(json.dumps(self.baseline()))
            with patch.object(guest,'WORK',work),patch.object(guest,'state',side_effect=[self.baseline(),self.mirrored()]),patch.object(guest,'run',side_effect=RuntimeError('simulated command failure')),patch.object(guest,'restore') as restore:
                with self.assertRaises(RuntimeError):guest.mirror()
                restore.assert_called_once()
                self.assertTrue((work/'mirror-failure.json').is_file())

    def test_backup_binary_not_in_command_log(self):
        source=ast.parse((ROOT/'automation/m2_mirror_guest_prepared.py').read_text())
        backup=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='backup')
        # Binary backup must bypass run(), whose public stdout is logged.
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='run' for n in ast.walk(backup)))
        self.assertNotIn("raw = run(",ast.get_source_segment((ROOT/'automation/m2_mirror_guest_prepared.py').read_text(),backup))

    def test_frame_case_generation_without_sockets(self):
        tree=ast.parse((ROOT/'automation/m2_tap_frame_test.py').read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        body=next(n.body for n in main.body if isinstance(n,ast.Try))
        for mirror,count in [(False,31),(True,32)]:
            calls=[]
            env={'a':SimpleNamespace(mirror=mirror),'VLANS':guest.VLAN,
                 'case':lambda *args,**kwargs:calls.append(args[0]),'results':calls,'expected_count':count}
            exec(compile(ast.fix_missing_locations(ast.Module(body=body,type_ignores=[])),'mock-case-enumeration','exec'),env)
            self.assertEqual(len(calls),count)
            self.assertEqual(len(set(calls)),count)
            self.assertTrue(env['complete'])

    def test_resource_gate_rejects_low_host_memory_and_other_vm(self):
        eve={'node':{'uuid':'core'},'qemu':[],'mem_available_kib':6500000,'swap_used_kib':0}
        with self.assertRaises(RuntimeError):queue.require_resources({'available_kib':500000,'virtual_available_kib':4000000},eve)
        eve['qemu']=[{'args':['foreign-vm']}]
        with self.assertRaises(RuntimeError):queue.require_resources({'available_kib':4000000,'virtual_available_kib':4000000},eve)

    def test_default_plan_does_not_call_remote_or_start_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'offline-plan'
            with patch.object(sys,'argv',['m2_run_queue.py','--run-dir',str(dest)]),patch.object(queue,'ssh',side_effect=AssertionError('Remote forbidden')),patch.object(queue.subprocess,'run',side_effect=AssertionError('Process forbidden')):
                queue.main()
            data=json.loads((dest/'queue.json').read_text())
            self.assertTrue(all(v['status']=='NOT_RUN' for v in data['stages'].values()))

    def test_clock_or_execute_flag_alone_cannot_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            q=queue.Queue(Path(tmp)/'blocked-run')
            with patch.object(queue,'ssh',side_effect=AssertionError('Remote forbidden')):
                with self.assertRaises(RuntimeError):queue.execute(q,SimpleNamespace(resources_ready=False))

    def test_console_quote_and_hash_validation(self):
        value="a'b $HOME `do-not-execute`"
        self.assertEqual(shlex.split(transport.ConsoleJob.quote(value)),[value])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'command-0042.txt').write_text('retained previous command')
            job=transport.ConsoleJob(Path(tmp),'mock',True)
            self.assertEqual(job.counter,42)
            job.payload_sha='fixture-payload-hash'
            reply={'rc':0,'stdout':'{"fixture_only":true}','stderr':''}
            blob=base64.b64encode(zlib.compress(json.dumps(reply).encode())).decode()
            header=base64.b64encode(struct.pack('>I32si',len(blob),hashlib.sha256(blob.encode()).digest(),0)).decode()
            commands=[]
            def fake_command(text):
                commands.append(text)
                parts=shlex.split(text)
                if parts[:2]==['python3','-c']:compile(parts[2],'prepared-remote-command','exec')
                return Path(tmp)/'not-an-evidence-image.png'
            with patch.object(job,'command',side_effect=fake_command),patch.object(transport,'decode',side_effect=[header,blob]):
                self.assertEqual(job.run('baseline','/root/m2-traffic-mock'),reply)
            bad=header
            with patch.object(job,'command',side_effect=fake_command),patch.object(transport,'decode',side_effect=[bad,blob[:-1]+'A']):
                with self.assertRaises(RuntimeError):job.run('verify','/root/m2-traffic-mock')

    def test_console_bundle_preserves_utf8_bytes_without_double_base64(self):
        with tempfile.TemporaryDirectory() as tmp:
            job=transport.ConsoleJob(Path(tmp),'mock-bundle',True)
            commands=[]
            def hash_screen(image,size):
                if commands[-1].startswith('printf %s '):return hashlib.sha256(shlex.split(commands[-1])[2].encode()).hexdigest()
                return job.payload_sha
            with patch.object(job,'command',side_effect=lambda text:commands.append(text)),patch.object(transport,'decode',side_effect=hash_screen):
                job.stage({'guest.py':'# kiem tra UTF-8: \u0111\u1ed3 \u00e1n\n'.encode('utf-8')})
            chunks=[shlex.split(c)[2] for c in commands if c.startswith('printf %s ')]
            raw=zlib.decompress(base64.b64decode(''.join(chunks)))
            self.assertEqual(json.loads(raw)['guest.py'].encode('utf-8'),'# kiem tra UTF-8: \u0111\u1ed3 \u00e1n\n'.encode('utf-8'))
            self.assertEqual(hashlib.sha256(raw).hexdigest(),job.payload_sha)
            compile(shlex.split(commands[-1])[2],'prepared-unpack-command','exec')
            token=base64.b64encode(bytes.fromhex(job.payload_sha)).decode()
            with patch.object(job,'command',return_value=Path(tmp)/'mock.png'),patch.object(transport,'decode',return_value=token):
                self.assertTrue(job.reuse({'guest.py':json.loads(raw)['guest.py'].encode('utf-8')}))
            with patch.object(job,'command',return_value=Path(tmp)/'mock.png'),patch.object(transport,'decode',return_value='A'*44):
                self.assertFalse(job.reuse({'guest.py':b'changed source'}))

    def test_proposed_address_plan_rejects_vip_in_dhcp_pool(self):
        data=json.loads((ROOT/'configs/M3/address-proposal.json').read_text())
        self.assertTrue(validate(data)['design_checks_ok'])
        self.assertFalse(validate(data)['deployable'])
        data['vlans'][1]['dhcp_proposed']=['192.168.40.1','192.168.40.199']
        with self.assertRaises(ValueError):validate(data)

    def test_qemu_tap_swap_rejected_even_if_all_macs_still_exist(self):
        recorded=json.loads((ROOT/'docs/evidence/M2/isolated-bridge-20261101/host-before.json').read_text(encoding='utf-8-sig'))
        args=recorded['qemu_processes'][0]['args']
        verify_qemu_mapping(args)
        swapped=[x.replace('ifname=vunl0_3_0,','ifname=swap,').replace('ifname=vunl0_3_1,','ifname=vunl0_3_0,').replace('ifname=swap,','ifname=vunl0_3_1,') for x in args]
        with self.assertRaises(AssertionError):verify_qemu_mapping(swapped)

    def test_benign_frame_checksums_without_sending(self):
        data=marker.frame()
        self.assertEqual(marker.checksum(data[14:34]),0)
        self.assertEqual(marker.checksum(data[34:]),0)
        self.assertIn(marker.MARKER,data)

    def test_mirror_created_atomically_and_capture_not_a_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);(work/'backup-metadata.json').write_text('{}')
            (work/'before.json').write_text(json.dumps(self.baseline()))
            with patch.object(guest,'WORK',work),patch.object(guest,'state',side_effect=[self.baseline(),self.mirrored()]),patch.object(guest,'run') as run:
                guest.mirror()
                command=run.call_args_list[0].args[0]
                self.assertIn('add-port',command);self.assertIn('output_port=@p7',command)
                self.assertEqual(next(x for x in command if x.startswith('select_src_port=')),
                                 'select_src_port=@p0,@p1,@p2,@p3,@p4,@p5,@p6')

    def test_requested_reboot_is_verified_without_requesting_another(self):
        with tempfile.TemporaryDirectory() as tmp:
            q=queue.Queue(Path(tmp)/'mock-resume')
            for stage in queue.STAGES:q.mark(stage,'DONE')
            q.mark('reboot','REQUESTED');q.mark('collect','NOT_RUN')
            q.data['initial_boot_id']='old-boot'
            eve={'node':{'uuid':'core'},'qemu':[{'args':['core']}],'mem_available_kib':4000000,'swap_used_kib':0}
            win=SimpleNamespace(stdout=json.dumps({'available_kib':4000000,'virtual_available_kib':4000000}))
            args=SimpleNamespace(resources_ready=True,console_shell_ready=True,reboot_ready=True)
            with patch.object(queue,'ssh',return_value=eve),patch.object(queue.subprocess,'run',return_value=win),patch.object(queue,'ConsoleJob') as adapter:
                adapter.return_value.session='mock-session'
                adapter.return_value.run.return_value={'stdout':json.dumps({'state':{'boot_id':'new-boot'}})}
                queue.execute(q,args)
                adapter.return_value.command.assert_not_called()
                self.assertTrue(q.done('reboot'));self.assertTrue(q.done('collect'))


if __name__=='__main__':unittest.main(verbosity=2)
