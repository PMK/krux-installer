'use strict'

import { join } from 'path'
import { createHash } from 'crypto'

import axios from 'axios'
import bufferedSpawn from 'buffered-spawn'
import createDebug from 'debug'

import { readFileAsync, existsAsync } from './utils/fs-async'
import Handler from './base'

const debug = createDebug('krux:verify-official-releases')

export default class VerifyOfficialReleasesHandler extends Handler {

  constructor (win, store) {
    super(win)
    this.url = 'https://api.github.com/repos/selfcustody/krux/git/refs/tags'
    this.headers = {
      'User-Agent': `Chrome/${process.versions.chrome}`
    }
    this.store = store
  }

  _info(msg) {
    debug(msg)
    if (typeof msg == 'object') {
      this.send('window:log:info', JSON.stringify(msg))
    } else {
      this.send('window:log:info', msg)
    }
  }

  async fetchReleases() {
    try {
      this._info(`fetching ${this.url}`)
      const response = await axios({
        method: 'get',
        url: this.url,
        headers: this.headers
      })
      if (response.status === 200) {
        this._info(response.data)
        return response.data
      } else {
        throw new Error(`${this.url} returned ${response.status} code`)
      }
    } catch (error) {
      this._info(error)
      this.send('official:releases:get:error', error)
    }
  }

  /*
   * verifyHash
   */
  async verifyHash () {
    const result = []
    const resources = this.store.get('resources')
    const version = this.store.get('version')
    const resource = version.split('tag/')[1]

    const zipFileRelPath = `${resource}/krux-${resource}.zip`
    const shaFileRelPath = `${resource}/krux-${resource}.zip.sha256.txt`

    const zipFilePath = join(resources, zipFileRelPath)
    const shaFilePath = join(resources, shaFileRelPath)

    // Maybe the sha256txt file could be downloade
    // after checking, so we will check if the file exists
    // and the string represenation is valid
    // every second, and then, return the result to client
    const verify = async (p) => {
      try {
        const exists = await existsAsync(p)
        const sha256buffer = await readFileAsync(shaFilePath, null)
        const sha256txt = sha256buffer.toString()
        if (exists && sha256txt !== '') {
          result.push({
            name: shaFileRelPath,
            value: sha256txt.replace(/[\n\t\r]/g,'')
          })

          const zipBuffer = await readFileAsync(zipFilePath, null)
          const hashSum = createHash('sha256')
          hashSum.update(zipBuffer)

          result.push({
            name: zipFileRelPath,
            value: hashSum.digest('hex')
          })

          const isMatch = result[0].value === result[1].value

          if (isMatch) {
            const msg = [
              'sha256sum match:',
              `${result[0].name} has a ${result[1].value} hash`,
              `and ${result[1].name} summed a hash ${result[1].value}.`
            ].join(' ')
            this._info(msg)
            this.send('official:releases:verified:hash', result)
          } else {
            const msg = [
              'sha256sum match error:',
              `${result[0].name} has a hash of ${result[0].value}`,
              `and ${result[1].name} summed a hash of ${result[1].value}`
            ].join(' ')
            const error = new Error(msg)
            this._info(error)
            this.send('official:releases:verified:hash:error', error)
          }
          clearInterval(interval)
        }
      } catch (error) {
        this._info(error)
        this.send('official:releases:verified:hash:error', error)
      }
    }
    this._info(`Verifying ${zipFilePath} against ${shaFilePath}`)
    const interval = setInterval(verify, 1000, shaFilePath)
  }

  async verifySign (options) {
    try {
      const resources = this.store.get('resources')

      const binPath = join(resources, options.bin)
      const pemPath = join(resources, options.pem)
      const sigPath =  join(resources, options.sig)


      this._info(`Verifying binary '${binPath}' against pem '${pemPath}' and signature '${sigPath}'`)

      // if platform is linux, use the same command
      // used in krux CLI. Else use sign-check package
      if (options.platform === 'linux' || options.platform === 'darwin') {
        const { stdout, stderr } = await bufferedSpawn('sh', [
          '-c',
          `openssl sha256 <${binPath} -binary | openssl pkeyutl -verify -pubin -inkey ${pemPath} -sigfile ${sigPath}`
        ])
        if (stderr !== null && stderr !== '') {
          this._info(stderr)
          this.send('official:releases:verified:sign:error', stderr)
        } else {
          this._info(stdout)
          this.send('official:releases:verified:sign', stdout)
        }
      } else {
        const err = new Error(`${options.platform} not implemented`)
        this.send('window:log:info', err)
        this.send('official:releases:verified:sign:error', err)
      }
    } catch (error) {
      this._info(error)
    }
  }
}
