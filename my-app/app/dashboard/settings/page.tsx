"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Slider } from "@/components/ui/slider"

interface ScoringWeights {
  values_weight: number
  cultural_weight: number
  cpm_weight: number
  rpm_weight: number
  views_to_subs_weight: number
}

export default function SettingsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [weights, setWeights] = useState<ScoringWeights>({
    values_weight: 20,
    cultural_weight: 10,
    cpm_weight: 20,
    rpm_weight: 20,
    views_to_subs_weight: 30
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!isLoading && !user) router.push("/login")
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      loadWeights()
    }
  }, [user])

  const loadWeights = async () => {
    if (!user) return
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:5000/api/auth/scoring-weights?user_id=${user.id}`)
      if (res.ok) {
        const data = await res.json()
        if (data.weights) {
          setWeights({
            values_weight: data.weights.values_weight * 100,
            cultural_weight: data.weights.cultural_weight * 100,
            cpm_weight: data.weights.cpm_weight * 100,
            rpm_weight: data.weights.rpm_weight * 100,
            views_to_subs_weight: data.weights.views_to_subs_weight * 100
          })
        }
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const saveWeights = async () => {
    if (!user) return
    setSaving(true)
    try {
      const res = await fetch(`http://localhost:5000/api/auth/scoring-weights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          values_weight: weights.values_weight / 100,
          cultural_weight: weights.cultural_weight / 100,
          cpm_weight: weights.cpm_weight / 100,
          rpm_weight: weights.rpm_weight / 100,
          views_to_subs_weight: weights.views_to_subs_weight / 100
        })
      })
      if (res.ok) {
        alert("Settings saved successfully!")
      } else {
        alert("Failed to save settings")
      }
    } catch (e) {
      console.error(e)
      alert("Failed to save settings")
    } finally {
      setSaving(false)
    }
  }

  const updateWeight = (key: keyof ScoringWeights, value: number[]) => {
    setWeights(prev => ({ ...prev, [key]: value[0] }))
  }

  const getTotalWeight = () => {
    return Object.values(weights).reduce((sum, weight) => sum + weight, 0)
  }

  const isTotalValid = () => {
    return Math.abs(getTotalWeight() - 100) < 0.1
  }

  if (isLoading || !user) return <div className="p-6">Loading...</div>

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Scoring Settings</h1>
        <p className="text-sm text-muted-foreground">
          Adjust the weights for different scoring factors. Total must equal 100%.
        </p>
      </div>

      <div className="space-y-8">
        {/* Values vs About */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Values vs About Match</label>
            <span className="text-sm text-muted-foreground">{weights.values_weight}%</span>
          </div>
          <Slider
            value={[weights.values_weight]}
            onValueChange={(value) => updateWeight('values_weight', value)}
            max={100}
            min={0}
            step={1}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How much to weight the alignment between company values and channel description
          </p>
        </div>

        {/* Cultural Fit */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Cultural Fit</label>
            <span className="text-sm text-muted-foreground">{weights.cultural_weight}%</span>
          </div>
          <Slider
            value={[weights.cultural_weight]}
            onValueChange={(value) => updateWeight('cultural_weight', value)}
            max={100}
            min={0}
            step={1}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How much to weight cultural compatibility between company and influencer countries
          </p>
        </div>

        {/* CPM */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">CPM (Cost Per Mille)</label>
            <span className="text-sm text-muted-foreground">{weights.cpm_weight}%</span>
          </div>
          <Slider
            value={[weights.cpm_weight]}
            onValueChange={(value) => updateWeight('cpm_weight', value)}
            max={100}
            min={0}
            step={1}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How much to weight CPM - lower CPM is better for cost efficiency
          </p>
        </div>

        {/* RPM */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">RPM (Revenue Per Mille)</label>
            <span className="text-sm text-muted-foreground">{weights.rpm_weight}%</span>
          </div>
          <Slider
            value={[weights.rpm_weight]}
            onValueChange={(value) => updateWeight('rpm_weight', value)}
            max={100}
            min={0}
            step={1}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How much to weight RPM - higher RPM preferred for luxury goods, lower for regular products
          </p>
        </div>

        {/* Views to Subs Ratio */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Views to Subscribers Ratio</label>
            <span className="text-sm text-muted-foreground">{weights.views_to_subs_weight}%</span>
          </div>
          <Slider
            value={[weights.views_to_subs_weight]}
            onValueChange={(value) => updateWeight('views_to_subs_weight', value)}
            max={100}
            min={0}
            step={1}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How much to weight the ratio of average views to subscribers - higher is better
          </p>
        </div>

        {/* Total Weight Display */}
        <div className="p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between">
            <span className="font-medium">Total Weight</span>
            <span className={`font-bold ${isTotalValid() ? 'text-green-600' : 'text-red-600'}`}>
              {getTotalWeight().toFixed(1)}%
            </span>
          </div>
          {!isTotalValid() && (
            <p className="text-sm text-red-600 mt-1">
              Total must equal 100% to save settings
            </p>
          )}
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={saveWeights}
            disabled={!isTotalValid() || saving}
            className="px-6 py-2 bg-primary text-primary-foreground rounded disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
