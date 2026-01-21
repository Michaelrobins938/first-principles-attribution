'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';

/** * INTERFACES: Fixed TS7006 by providing explicit structures
 */
interface Node3D { id: string; x: number; y: number; z: number; color: string; }
interface Link { source: string; target: string; value: number; }
interface BootstrapCI { p05: number; p50: number; p95: number; }
interface AlphaSweepData { alpha: number; values: Record<string, number>; }

interface HybridAttributionDashboardProps {
  className?: string;
}

// 3D Journey Graph Component
function Journey3D() {
  const [hovered, setHovered] = useState<string | null>(null);

  const nodes: Node3D[] = [
    { id: "START", x: -3, y: 0, z: 0, color: "#f59e0b" },
    { id: "Google_Search", x: -1, y: 2, z: 1, color: "#4285F4" },
    { id: "Direct", x: 0, y: 0, z: 2, color: "#34A853" },
    { id: "Facebook", x: 1, y: -2, z: -1, color: "#1877F2" },
    { id: "Email", x: 2, y: 1, z: 0.5, color: "#EA4335" },
    { id: "CONVERSION", x: 4, y: 0, z: 0, color: "#f59e0b" }
  ];

  const links: Link[] = [
    { source: "START", target: "Google_Search", value: 1.0 },
    { source: "Google_Search", target: "Direct", value: 1.0 },
    { source: "Direct", target: "Facebook", value: 1.0 },
    { source: "Facebook", target: "Email", value: 1.0 },
    { source: "Email", target: "CONVERSION", value: 1.0 }
  ];

  const getTooltip = (id: string) => {
    const tooltips: Record<string, string> = {
      "START": "Initial touchpoint - user discovers the product",
      "Google_Search": "High-intent search for 'SaaS project management tools'",
      "Direct": "Direct visit to pricing page - conversion point",
      "Facebook": "Retargeting ad during consideration phase",
      "Email": "Nurture campaign reinforcing value proposition",
      "CONVERSION": "Final purchase completion"
    };
    return tooltips[id] || id;
  };

  return (
    <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
      <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />

      {nodes.map((node) => (
        <mesh
          key={node.id}
          position={[node.x, node.y, node.z]}
          onPointerOver={() => setHovered(node.id)}
          onPointerOut={() => setHovered(null)}
        >
          <sphereGeometry args={[0.5, 16, 16]} />
          <meshStandardMaterial color={hovered === node.id ? "#ffffff" : node.color} />
          <Html position={[0, 0.8, 0]} center>
            <div style={{ color: 'white', fontSize: '12px', fontWeight: 'bold', textAlign: 'center' }}>
              {node.id.replace('_', '\n')}
            </div>
          </Html>
          {hovered === node.id && (
            <Html position={[0, 1.5, 0]} center>
              <div style={{
                background: 'rgba(0,0,0,0.8)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                maxWidth: '150px',
                textAlign: 'center'
              }}>
                {getTooltip(node.id)}
              </div>
            </Html>
          )}
        </mesh>
      ))}

      {links.map((link, i) => {
        const sourceNode = nodes.find(n => n.id === link.source)!;
        const targetNode = nodes.find(n => n.id === link.target)!;
        const points = [sourceNode, targetNode].map(n => new THREE.Vector3(n.x, n.y, n.z));
        const curve = new THREE.CatmullRomCurve3(points);
        const geometry = new THREE.TubeGeometry(curve, 20, 0.05, 8, false);

        return (
          <mesh key={i} geometry={geometry}>
            <meshStandardMaterial color="#f59e0b" />
          </mesh>
        );
      })}
    </Canvas>
  );
}

export default function HybridAttributionDashboard({ className = '' }: HybridAttributionDashboardProps) {
  const [alphaVal, setAlphaVal] = useState(0.5);

  const initCharts = async () => {
    if (typeof window === 'undefined') return;
    try {
    const d3 = await import('d3');

    // Clear existing SVGs
    d3.selectAll("#journey-graph svg, #alpha-sweep svg").remove();
    d3.select("#stats-table-body").selectAll("*").remove();

    const colors: Record<string, string> = {
      "Google_Search": "#4285F4",
      "Facebook": "#1877F2",
      "Email": "#EA4335",
      "Direct": "#34A853"
    };

    const demoData = {
      channels: ["Google_Search", "Facebook", "Email", "Direct"],
      markov_value: { "Google_Search": 83.7, "Facebook": 20.25, "Email": 24.3, "Direct": 6.75 } as Record<string, number>,
      shapley_value: { "Google_Search": 63.0, "Facebook": 27.0, "Email": 43.5, "Direct": 16.5 } as Record<string, number>,
      markov_share: { "Google_Search": 0.558, "Facebook": 0.135, "Email": 0.162, "Direct": 0.045 } as Record<string, number>,
      alpha_sweep_values: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      alpha_sweep_data: {
        "Google_Search": [63.00, 65.07, 67.14, 69.21, 71.28, 73.35, 75.42, 77.49, 79.56, 81.63, 83.70],
        "Facebook": [27.00, 26.325, 25.65, 24.975, 24.30, 23.625, 22.95, 22.275, 21.60, 20.925, 20.25],
        "Email": [43.50, 41.85, 40.20, 38.55, 36.90, 33.90, 31.41, 29.01, 26.73, 25.56, 24.30],
        "Direct": [16.50, 16.6575, 16.815, 16.9725, 17.13, 11.625, 14.265, 14.8725, 15.48, 16.1925, 16.50]
      } as Record<string, number[]>,
      bootstrap_ci: {
        "Google_Search": { "p05": 68.4, "p50": 73.35, "p95": 78.3 },
        "Facebook": { "p05": 20.1, "p50": 23.625, "p95": 26.5 },
        "Email": { "p05": 30.6, "p50": 33.9, "p95": 37.8 },
        "Direct": { "p05": 8.25, "p50": 11.625, "p95": 14.5 }
      } as Record<string, BootstrapCI>
    };

    // Journey data from sample_journeys.json
    const journeyData = {
      journeys: [
        { journey_id: "journey-001", path: [{ channel: "Search" }, { channel: "Social" }, { channel: "Email" }], conversion: true, conversion_value: 100.00, num_touchpoints: 3, duration_hours: 4.5 },
        { journey_id: "journey-002", path: [{ channel: "Direct" }], conversion: true, conversion_value: 50.00, num_touchpoints: 1, duration_hours: 0.0 },
        { journey_id: "journey-003", path: [{ channel: "Paid" }, { channel: "Search" }], conversion: false, conversion_value: 0.00, num_touchpoints: 2, duration_hours: 3.0 },
        { journey_id: "journey-004", path: [{ channel: "Email" }, { channel: "Direct" }], conversion: true, conversion_value: 200.00, num_touchpoints: 2, duration_hours: 8.0 },
        { journey_id: "journey-005", path: [{ channel: "Social" }, { channel: "Paid" }, { channel: "Email" }, { channel: "Direct" }], conversion: true, conversion_value: 75.00, num_touchpoints: 4, duration_hours: 23.0 }
      ]
    };

    // Build channel statistics from journey data
    const channelStats: Record<string, { touchpoints: number; conversions: number; value: number; journeys: string[] }> = {};
    journeyData.journeys.forEach(j => {
      j.path.forEach(p => {
        if (!channelStats[p.channel]) {
          channelStats[p.channel] = { touchpoints: 0, conversions: 0, value: 0, journeys: [] };
        }
        channelStats[p.channel].touchpoints++;
        if (j.conversion) {
          channelStats[p.channel].conversions++;
          channelStats[p.channel].value += j.conversion_value / j.path.length;
        }
        if (!channelStats[p.channel].journeys.includes(j.journey_id)) {
          channelStats[p.channel].journeys.push(j.journey_id);
        }
      });
    });

    const channelColors: Record<string, string> = {
      "Search": "#4285f4",
      "Social": "#1877F2",
      "Email": "#EA4335",
      "Direct": "#34A853",
      "Paid": "#f59e0b"
    };

    // 1. Radial Tree Visualization - Journey Channel Hierarchy
    const drawRadialTree = () => {
      const canvas = document.getElementById('radial-tree-canvas') as HTMLCanvasElement;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      let rotation = 0;
      let autoRotate = true;
      let hoveredNode: any = null;
      let cx = 0, cy = 0;

      // Build tree from journey data
      const totalValue = journeyData.journeys.reduce((sum, j) => sum + j.conversion_value, 0);
      const totalJourneys = journeyData.journeys.length;

      const tree = {
        id: 'root',
        name: 'Journeys',
        value: totalJourneys,
        displayValue: `$${totalValue}`,
        depth: 0,
        color: '#8b5cf6',
        children: Object.entries(channelStats).map(([channel, stats]) => ({
          id: channel.toLowerCase(),
          name: channel,
          value: stats.touchpoints,
          displayValue: `$${Math.round(stats.value)}`,
          color: channelColors[channel] || '#6366f1',
          depth: 1,
          children: stats.journeys.map(jId => {
            const journey = journeyData.journeys.find(j => j.journey_id === jId)!;
            return {
              id: `${channel}-${jId}`,
              name: jId.replace('journey-', 'J'),
              value: journey.conversion_value,
              displayValue: journey.conversion ? `$${journey.conversion_value}` : 'No Conv',
              color: journey.conversion ? channelColors[channel] : '#6b7280',
              depth: 2
            };
          })
        }))
      };

      const lighten = (hex: string, amt: number) => {
        let r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
        r = Math.min(255, r + amt); g = Math.min(255, g + amt); b = Math.min(255, b + amt);
        return `rgb(${r},${g},${b})`;
      };

      const resize = () => {
        const rect = canvas.parentElement?.getBoundingClientRect();
        if (!rect) return;
        canvas.width = rect.width - 48;
        canvas.height = 500;
        cx = canvas.width / 2;
        cy = canvas.height / 2;
      };

      // Optimized radii for better spacing
      const getRadius = (depth: number) => {
        const baseRadius = Math.min(cx, cy) * 0.85;
        if (depth === 0) return 0;
        if (depth === 1) return baseRadius * 0.45;
        return baseRadius * 0.85;
      };

      const getNodeSize = (depth: number) => {
        if (depth === 0) return 40;
        if (depth === 1) return 28;
        return 18;
      };

      const forEachNode = (node: any, callback: Function, parentAngle = 0, angleSpan = Math.PI * 2, depth = 0) => {
        const radius = getRadius(depth);
        const angle = parentAngle + rotation;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;
        const r = getNodeSize(depth);
        callback(node, x, y, r, angle, depth);
        if (node.children) {
          const childSpan = angleSpan / node.children.length;
          node.children.forEach((child: any, i: number) => {
            const childAngle = parentAngle - angleSpan / 2 + childSpan * (i + 0.5);
            forEachNode(child, callback, childAngle, childSpan * 0.7, depth + 1);
          });
        }
      };

      const handleHover = (e: MouseEvent) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left, my = e.clientY - rect.top;
        hoveredNode = null;
        forEachNode(tree, (node: any, x: number, y: number, r: number) => {
          if (Math.hypot(x - mx, y - my) < r + 5) hoveredNode = node;
        });
      };

      const draw = () => {
        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        if (autoRotate) rotation += 0.002;

        // Draw orbital rings with dynamic radii
        [getRadius(1), getRadius(2)].forEach(r => {
          if (r > 0) {
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(99, 102, 241, 0.12)';
            ctx.setLineDash([5, 5]);
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.setLineDash([]);
          }
        });

        // Draw connections first
        forEachNode(tree, (node: any, x: number, y: number, r: number, angle: number, depth: number) => {
          if (node.children) {
            node.children.forEach((child: any, i: number) => {
              const childRadius = getRadius(depth + 1);
              const childSpan = (Math.PI * 2) / node.children.length;
              const baseAngle = depth === 0 ? -Math.PI / 2 : angle - rotation;
              const childAngle = baseAngle - (Math.PI * 2 / node.children.length) / 2 + childSpan * (i + 0.5) + rotation;
              const childX = cx + Math.cos(childAngle) * childRadius;
              const childY = cy + Math.sin(childAngle) * childRadius;

              // Curved connection with gradient
              ctx.beginPath();
              ctx.moveTo(x, y);
              const midX = (x + childX) / 2, midY = (y + childY) / 2;
              const cpX = midX + (childY - y) * 0.15, cpY = midY - (childX - x) * 0.15;
              ctx.quadraticCurveTo(cpX, cpY, childX, childY);
              const isHovered = hoveredNode === node || hoveredNode === child;
              ctx.strokeStyle = isHovered ? (child.color || 'rgba(139, 92, 246, 0.9)') : 'rgba(139, 92, 246, 0.25)';
              ctx.lineWidth = isHovered ? 3 : 1.5;
              ctx.stroke();
            });
          }
        });

        // Draw nodes
        const drawn = new Set();
        forEachNode(tree, (node: any, x: number, y: number, r: number, angle: number, depth: number) => {
          if (drawn.has(node.id)) return;
          drawn.add(node.id);

          const isHovered = hoveredNode === node;

          // Glow
          if (isHovered) {
            const grad = ctx.createRadialGradient(x, y, 0, x, y, r * 2.5);
            grad.addColorStop(0, (node.color || '#8b5cf6') + '66');
            grad.addColorStop(1, 'transparent');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(x, y, r * 2.5, 0, Math.PI * 2);
            ctx.fill();
          }

          // Node
          const grad = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, 0, x, y, r);
          grad.addColorStop(0, lighten(node.color || '#8b5cf6', 30));
          grad.addColorStop(1, node.color || '#8b5cf6');
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
          ctx.strokeStyle = isHovered ? '#fff' : 'rgba(255,255,255,0.3)';
          ctx.lineWidth = isHovered ? 2 : 1;
          ctx.stroke();

          // Label
          ctx.fillStyle = '#fff';
          ctx.font = depth === 0 ? 'bold 14px system-ui' : (depth === 1 ? 'bold 12px system-ui' : '10px system-ui');
          ctx.textAlign = 'center';
          ctx.fillText(node.name, x, y + r + 18);

          // Show value/displayValue
          ctx.fillStyle = depth === 0 ? '#f59e0b' : '#9ca3af';
          ctx.font = depth === 0 ? 'bold 11px system-ui' : '9px system-ui';
          const valueText = node.displayValue || (node.value > 0 ? node.value.toLocaleString() : '');
          if (valueText) {
            ctx.fillText(valueText, x, y + r + 30);
          }

          // Hover tooltip
          if (isHovered && depth > 0) {
            const tooltipY = y - r - 40;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
            ctx.roundRect(x - 60, tooltipY - 12, 120, 28, 6);
            ctx.fill();
            ctx.strokeStyle = node.color || '#8b5cf6';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 10px system-ui';
            ctx.fillText(`${node.name}: ${node.displayValue || node.value}`, x, tooltipY + 4);
          }
        });
      };

      // Setup controls
      const rotateBtn = document.getElementById('tree-rotate');
      rotateBtn?.addEventListener('click', () => {
        autoRotate = !autoRotate;
        rotateBtn.textContent = autoRotate ? 'Auto-Rotate: On' : 'Auto-Rotate: Off';
        rotateBtn.classList.toggle('border-purple-500', autoRotate);
        rotateBtn.classList.toggle('border-gray-600', !autoRotate);
      });

      canvas.addEventListener('mousemove', handleHover);
      canvas.addEventListener('mouseleave', () => { hoveredNode = null; });

      resize();
      let animationId: number;

      const animate = () => {
        draw();
        animationId = requestAnimationFrame(animate);
      };
      animate();

      const handleResize = () => resize();
      window.addEventListener('resize', handleResize);

      return () => {
        cancelAnimationFrame(animationId);
        window.removeEventListener('resize', handleResize);
      };
    };

    // 3. Parallel Coordinates Visualization (Canvas-based) - Journey Data
    const drawParallelCoordinates = () => {
      const canvas = document.getElementById('parallel-canvas') as HTMLCanvasElement;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Channel list for mapping
      const channels = ['Search', 'Social', 'Email', 'Direct', 'Paid'];

      // Transform journey data into parallel coordinate points
      // Each touchpoint becomes a data point showing its context in the journey
      const points: any[] = [];
      journeyData.journeys.forEach((journey, jIdx) => {
        journey.path.forEach((touchpoint, tIdx) => {
          points.push({
            journeyId: jIdx,
            channel: touchpoint.channel,
            touchpointIndex: tIdx,
            totalTouchpoints: journey.num_touchpoints,
            durationHours: journey.duration_hours,
            conversionValue: journey.conversion_value,
            converted: journey.conversion ? 1 : 0,
            position: tIdx / Math.max(1, journey.num_touchpoints - 1), // 0 to 1 position in journey
            color: channelColors[touchpoint.channel] || '#8b5cf6'
          });
        });
      });

      const axes = ['Channel', 'Position', 'Touchpoints', 'Duration (h)', 'Value ($)', 'Converted'];
      let selectedChannel = 'all';
      let opacity = 0.5;

      const hexToRgba = (hex: string, alpha: number) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
      };

      const resize = () => {
        const rect = canvas.parentElement?.getBoundingClientRect();
        if (!rect) return;
        canvas.width = rect.width - 48;
        canvas.height = 420;
      };

      // Calculate max values for normalization
      const maxTouchpoints = Math.max(...journeyData.journeys.map(j => j.num_touchpoints));
      const maxDuration = Math.max(...journeyData.journeys.map(j => j.duration_hours));
      const maxValue = Math.max(...journeyData.journeys.map(j => j.conversion_value));

      let hoveredPoint: any = null;

      const draw = () => {
        const margin = { left: 80, right: 50, top: 50, bottom: 70 };
        const innerWidth = canvas.width - margin.left - margin.right;
        const innerHeight = canvas.height - margin.top - margin.bottom;

        ctx.fillStyle = '#0a0a0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const axisSpacing = innerWidth / (axes.length - 1);

        // Draw axes with better styling
        axes.forEach((axis, i) => {
          const x = margin.left + i * axisSpacing;

          // Axis line
          ctx.beginPath();
          ctx.moveTo(x, margin.top);
          ctx.lineTo(x, margin.top + innerHeight);
          ctx.strokeStyle = 'rgba(255,255,255,0.25)';
          ctx.lineWidth = 2;
          ctx.stroke();

          // Axis tick marks
          for (let t = 0; t <= 4; t++) {
            const tickY = margin.top + (t / 4) * innerHeight;
            ctx.beginPath();
            ctx.moveTo(x - 5, tickY);
            ctx.lineTo(x + 5, tickY);
            ctx.strokeStyle = 'rgba(255,255,255,0.3)';
            ctx.lineWidth = 1;
            ctx.stroke();
          }

          // Axis labels at top
          ctx.fillStyle = '#f59e0b';
          ctx.font = 'bold 11px system-ui';
          ctx.textAlign = 'center';
          ctx.fillText(axis, x, margin.top - 15);

          // Min/Max labels
          ctx.fillStyle = '#6b7280';
          ctx.font = '9px system-ui';
          if (i === 0) {
            ctx.textAlign = 'right';
            ctx.fillText('Search', x - 10, margin.top + 5);
            ctx.fillText('Paid', x - 10, margin.top + innerHeight);
          }
        });

        // Draw lines for each touchpoint (grouped by journey)
        const journeyGroups: Record<number, any[]> = {};
        points.forEach(p => {
          if (!journeyGroups[p.journeyId]) journeyGroups[p.journeyId] = [];
          journeyGroups[p.journeyId].push(p);
        });

        // Draw each journey's path
        Object.values(journeyGroups).forEach(journeyPoints => {
          journeyPoints.forEach(p => {
            if (selectedChannel !== 'all' && p.channel !== selectedChannel) return;

            const values = [
              channels.indexOf(p.channel) / (channels.length - 1),
              p.position,
              (p.totalTouchpoints - 1) / (maxTouchpoints - 1),
              p.durationHours / maxDuration,
              p.conversionValue / maxValue,
              p.converted
            ];

            ctx.beginPath();
            values.forEach((v, i) => {
              const x = margin.left + i * axisSpacing;
              const y = margin.top + (1 - v) * innerHeight;
              if (i === 0) ctx.moveTo(x, y);
              else ctx.lineTo(x, y);
            });

            const isHovered = hoveredPoint && hoveredPoint.journeyId === p.journeyId;
            ctx.strokeStyle = hexToRgba(p.color, isHovered ? 0.9 : opacity);
            ctx.lineWidth = isHovered ? 3 : 2;
            ctx.stroke();

            // Draw points on axes
            values.forEach((v, i) => {
              const x = margin.left + i * axisSpacing;
              const y = margin.top + (1 - v) * innerHeight;
              ctx.beginPath();
              ctx.arc(x, y, isHovered ? 5 : 3, 0, Math.PI * 2);
              ctx.fillStyle = p.color;
              ctx.fill();
              if (isHovered) {
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
              }
            });
          });
        });

        // Legend
        const legendX = canvas.width - 120;
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.roundRect(legendX - 10, 10, 115, channels.length * 18 + 15, 6);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 10px system-ui';
        ctx.textAlign = 'left';
        ctx.fillText('Channels', legendX, 25);
        channels.forEach((ch, i) => {
          ctx.fillStyle = channelColors[ch];
          ctx.fillRect(legendX, 32 + i * 18, 10, 10);
          ctx.fillStyle = '#9ca3af';
          ctx.font = '9px system-ui';
          ctx.fillText(ch, legendX + 15, 40 + i * 18);
        });
      };

      // Setup controls
      const channelFilter = document.getElementById('cluster-filter') as HTMLSelectElement;
      const lineOpacity = document.getElementById('line-opacity') as HTMLInputElement;

      channelFilter?.addEventListener('change', (e) => {
        selectedChannel = (e.target as HTMLSelectElement).value;
        draw();
      });

      lineOpacity?.addEventListener('input', (e) => {
        opacity = parseFloat((e.target as HTMLInputElement).value);
        draw();
      });

      // Hover interaction
      canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const margin = { left: 80, right: 50, top: 50, bottom: 70 };
        const innerHeight = canvas.height - margin.top - margin.bottom;
        const axisSpacing = (canvas.width - margin.left - margin.right) / (axes.length - 1);

        hoveredPoint = null;
        points.forEach(p => {
          const values = [
            channels.indexOf(p.channel) / (channels.length - 1),
            p.position,
            (p.totalTouchpoints - 1) / (maxTouchpoints - 1),
            p.durationHours / maxDuration,
            p.conversionValue / maxValue,
            p.converted
          ];
          values.forEach((v, i) => {
            const x = margin.left + i * axisSpacing;
            const y = margin.top + (1 - v) * innerHeight;
            if (Math.hypot(x - mx, y - my) < 8) {
              hoveredPoint = p;
            }
          });
        });
        draw();
      });

      canvas.addEventListener('mouseleave', () => {
        hoveredPoint = null;
        draw();
      });

      resize();
      draw();

      const handleResize = () => { resize(); draw(); };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
      };
    };

    // 4. Animated Flow/Sankey Visualization
    const drawFlowViz = () => {
      const canvas = document.getElementById('flow-canvas') as HTMLCanvasElement;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      let particles: Array<{ flowIdx: number; t: number; speed: number; offset: number }> = [];
      let animationId: number;

      const flows = [
        { from: { x: 100, y: 145, name: 'Google Search' }, to: { x: 500, y: 125, name: 'Google Search' }, value: demoData.markov_value['Google_Search'] || 40, color: '#4285F4' },
        { from: { x: 100, y: 145, name: 'Google Search' }, to: { x: 500, y: 225, name: 'Facebook' }, value: 8, color: '#f97316' },
        { from: { x: 100, y: 225, name: 'Facebook' }, to: { x: 500, y: 125, name: 'Google Search' }, value: 10, color: '#1877F2' },
        { from: { x: 100, y: 225, name: 'Facebook' }, to: { x: 500, y: 225, name: 'Facebook' }, value: demoData.markov_value['Facebook'] || 25, color: '#1877F2' },
        { from: { x: 100, y: 305, name: 'Email' }, to: { x: 500, y: 305, name: 'Email' }, value: demoData.markov_value['Email'] || 20, color: '#EA4335' },
        { from: { x: 100, y: 385, name: 'Direct' }, to: { x: 500, y: 385, name: 'Direct' }, value: demoData.markov_value['Direct'] || 15, color: '#34A853' }
      ];

      // Add scaled positions
      const flowsWithScale = flows.map(f => ({
        ...f,
        from: { ...f.from, xScaled: f.from.x },
        to: { ...f.to, xScaled: f.to.x }
      }));

      const resize = () => {
        const rect = canvas.parentElement?.getBoundingClientRect();
        if (!rect) return;
        canvas.width = rect.width - 48;
        canvas.height = 450;
        const scaleX = canvas.width / 600;
        flowsWithScale.forEach(f => {
          f.from.xScaled = f.from.x * scaleX;
          f.to.xScaled = f.to.x * scaleX;
        });
      };

      const initParticles = () => {
        particles = [];
        flowsWithScale.forEach((flow, fi) => {
          const count = Math.ceil(flow.value / 5);
          for (let i = 0; i < count; i++) {
            particles.push({
              flowIdx: fi,
              t: Math.random(),
              speed: 0.002 + Math.random() * 0.002,
              offset: (Math.random() - 0.5) * (flow.value / 5)
            });
          }
        });
      };

      const bezierPoint = (p0: number, p1: number, p2: number, p3: number, t: number) => {
        const mt = 1 - t;
        return mt * mt * mt * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t * t * t * p3;
      };

      const hexToRgba = (hex: string, alpha: number) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
      };

      const draw = () => {
        ctx.fillStyle = 'rgba(10, 10, 15, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw flow paths
        flowsWithScale.forEach(flow => {
          const width = Math.max(2, flow.value / 5);
          ctx.beginPath();
          ctx.moveTo(flow.from.xScaled, flow.from.y);
          const cpx1 = flow.from.xScaled + (flow.to.xScaled - flow.from.xScaled) * 0.4;
          const cpx2 = flow.from.xScaled + (flow.to.xScaled - flow.from.xScaled) * 0.6;
          ctx.bezierCurveTo(cpx1, flow.from.y, cpx2, flow.to.y, flow.to.xScaled, flow.to.y);
          ctx.strokeStyle = hexToRgba(flow.color, 0.15);
          ctx.lineWidth = width;
          ctx.stroke();
        });

        // Draw particles
        particles.forEach(p => {
          const flow = flowsWithScale[p.flowIdx];
          const t = p.t;
          const x = bezierPoint(
            flow.from.xScaled,
            flow.from.xScaled + (flow.to.xScaled - flow.from.xScaled) * 0.4,
            flow.from.xScaled + (flow.to.xScaled - flow.from.xScaled) * 0.6,
            flow.to.xScaled,
            t
          );
          const y = bezierPoint(flow.from.y, flow.from.y, flow.to.y, flow.to.y, t) + p.offset;

          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fillStyle = flow.color;
          ctx.fill();

          p.t += p.speed;
          if (p.t > 1) p.t = 0;
        });

        // Draw labels
        const labels = new Set<string>();
        flowsWithScale.forEach(f => {
          labels.add(JSON.stringify({ name: f.from.name, x: f.from.xScaled, y: f.from.y }));
          labels.add(JSON.stringify({ name: f.to.name, x: f.to.xScaled, y: f.to.y }));
        });

        ctx.font = '13px system-ui, sans-serif';
        ctx.fillStyle = '#fff';
        labels.forEach(l => {
          const { name, x, y } = JSON.parse(l);
          ctx.textAlign = x < canvas.width / 2 ? 'right' : 'left';
          ctx.fillText(name, x < canvas.width / 2 ? x - 20 : x + 20, y + 4);
        });
      };

      const animate = () => {
        draw();
        animationId = requestAnimationFrame(animate);
      };

      resize();
      initParticles();
      animate();

      window.addEventListener('resize', resize);

      // Return cleanup function
      return () => {
        cancelAnimationFrame(animationId);
        window.removeEventListener('resize', resize);
      };
    };

    drawRadialTree();
    drawParallelCoordinates();
    drawFlowViz();

    // Populate Stats Table
    const tbody = d3.select("#stats-table-body");
    demoData.channels.forEach(ch => {
      const hybridValue = (demoData.markov_value[ch] + demoData.shapley_value[ch]) / 2;
      const ciRange = demoData.bootstrap_ci[ch].p95 - demoData.bootstrap_ci[ch].p05;
      const confidence = ciRange < 10 ? "High" : ciRange < 15 ? "Mid" : "Low";

      const row = tbody.append("tr");
      row.append("td").text(ch.replace("_", " ")).style("color", colors[ch]);
      row.append("td").text(((demoData.markov_share[ch] || 0) * 100).toFixed(1) + "%");
      row.append("td").text("$" + hybridValue.toFixed(2));
      row.append("td").text(`$${demoData.bootstrap_ci[ch].p05.toFixed(0)}–$${demoData.bootstrap_ci[ch].p95.toFixed(0)}`);
      row.append("td").text(confidence);
    });
    } catch (error) {
      console.error('Error in initCharts:', error);
    }
  };

  const [showMethodology, setShowMethodology] = useState(false);

  useEffect(() => {
    initCharts();
  }, [alphaVal]);

  return (
    <div className="p-6 md:p-8 bg-black text-white min-h-screen">
      {/* Hero Section - What is this? */}
      <div className="mb-10 border-b border-gray-800 pb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-amber-500 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🧠</span>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  First-Principles Attribution Engine
                </h1>
                <p className="text-amber-500 text-sm font-mono">Personal Epistemic Instrument v1.0.0</p>
              </div>
            </div>
            <p className="text-gray-400 max-w-2xl leading-relaxed">
              A <span className="text-white font-medium">thinking instrument</span> that transforms your behavioral data into
              actionable insights using rigorous mathematical models. Unlike black-box analytics, every calculation
              is transparent, defensible, and grounded in first principles.
            </p>
          </div>
          <button
            onClick={() => setShowMethodology(!showMethodology)}
            className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm hover:border-amber-500/50 transition-all flex items-center gap-2"
          >
            <span>{showMethodology ? '📖' : '❓'}</span>
            {showMethodology ? 'Hide Methodology' : 'How Does This Work?'}
          </button>
        </div>

        {/* Expandable Methodology Section */}
        {showMethodology && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in">
            {/* Markov Chains */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg overflow-hidden group hover:border-blue-500/50 transition-all">
              <div className="relative aspect-video bg-gradient-to-br from-blue-950 to-gray-900 overflow-hidden">
                <video
                  className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity scale-105 group-hover:scale-100 transition-transform duration-500"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source src="/videos/grok-video-0f69d54a-6e8e-4243-80f2-485c3829f5fc.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-blue-400 text-xl">⛓️</span>
                    <h3 className="font-bold text-white">Markov Chains</h3>
                  </div>
                  <p className="text-xs text-blue-200/80">Causality & Removal Effect</p>
                </div>
              </div>
              <div className="p-4">
                <p className="text-xs text-gray-400 mb-2">Answers: <span className="text-white">&quot;What caused the outcome?&quot;</span></p>
                <p className="text-xs text-gray-500">
                  Models the probability of moving between channels. The &quot;Removal Effect&quot; measures how much
                  conversion drops if we remove a channel entirely—revealing true causal impact.
                </p>
              </div>
            </div>

            {/* Shapley Values */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg overflow-hidden group hover:border-green-500/50 transition-all">
              <div className="relative aspect-video bg-gradient-to-br from-green-950 to-gray-900 overflow-hidden">
                <video
                  className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity scale-105 group-hover:scale-100 transition-transform duration-500"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source src="/videos/grok-video-f9990f12-8277-4fc9-a747-5ba7c7a863d1.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-green-400 text-xl">⚖️</span>
                    <h3 className="font-bold text-white">Shapley Values</h3>
                  </div>
                  <p className="text-xs text-green-200/80">Fair Credit Distribution</p>
                </div>
              </div>
              <div className="p-4">
                <p className="text-xs text-gray-400 mb-2">Answers: <span className="text-white">&quot;How should credit be fairly distributed?&quot;</span></p>
                <p className="text-xs text-gray-500">
                  From cooperative game theory. Considers every possible combination of channels to calculate
                  each one&apos;s marginal contribution. Guarantees axiomatic fairness—no channel is over/under-credited.
                </p>
              </div>
            </div>

            {/* Psychographic Priors */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg overflow-hidden group hover:border-purple-500/50 transition-all">
              <div className="relative aspect-video bg-gradient-to-br from-purple-950 to-gray-900 overflow-hidden">
                <video
                  className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity scale-105 group-hover:scale-100 transition-transform duration-500"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source src="/videos/grok-video-7b9f6453-6bb9-4746-9a64-223e82bda5b9.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-purple-400 text-xl">🎭</span>
                    <h3 className="font-bold text-white">Psychographic Priors</h3>
                  </div>
                  <p className="text-xs text-purple-200/80">Intent Quality Weighting</p>
                </div>
              </div>
              <div className="p-4">
                <p className="text-xs text-gray-400 mb-2">Answers: <span className="text-white">&quot;What was the intent quality?&quot;</span></p>
                <p className="text-xs text-gray-500">
                  Weights transitions by declared context (e.g., &quot;high-intent search&quot; = 1.5x).
                  <span className="text-amber-400"> Note: We never infer mental states</span>—only use explicitly declared context.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Alpha Control with Better Explanation */}
      <div className="mb-8 bg-gradient-to-r from-gray-900 to-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-amber-500">α</span> Blend Parameter
              <span className="text-xs bg-gray-800 px-2 py-1 rounded-full text-gray-400 ml-2">
                Current: {alphaVal.toFixed(1)}
              </span>
            </h2>
            <p className="text-xs text-gray-500 mt-1">Control the balance between causality and fairness in attribution</p>
          </div>
          <div className="text-right text-xs">
            <div className="text-gray-400">Formula: <code className="text-amber-400">Hybrid = α·Markov + (1-α)·Shapley</code></div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-green-400 whitespace-nowrap">⚖️ Shapley<br/><span className="text-xs text-gray-500">(Pure Fairness)</span></span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={alphaVal}
            onChange={(e) => setAlphaVal(parseFloat(e.target.value))}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
          <span className="text-sm text-blue-400 whitespace-nowrap">⛓️ Markov<br/><span className="text-xs text-gray-500">(Pure Causality)</span></span>
        </div>
        <div className="mt-3 text-xs text-gray-500 text-center">
          {alphaVal === 0 && "📊 Full Shapley: Every channel gets credit proportional to its marginal contribution across all coalitions"}
          {alphaVal === 0.5 && "🎯 Balanced: Equal weight to causal impact and fair distribution (recommended for most analyses)"}
          {alphaVal === 1 && "🔬 Full Markov: Credit based purely on removal effect—what happens if this channel didn't exist?"}
          {alphaVal !== 0 && alphaVal !== 0.5 && alphaVal !== 1 && `⚡ Custom blend: ${Math.round(alphaVal * 100)}% causal weight, ${Math.round((1-alphaVal) * 100)}% fairness weight`}
        </div>
      </div>

      {/* Key Metrics Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-white">5</div>
          <div className="text-xs text-gray-500">Total Journeys</div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">$425</div>
          <div className="text-xs text-gray-500">Total Revenue</div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-amber-400">80%</div>
          <div className="text-xs text-gray-500">Conversion Rate</div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-400">5</div>
          <div className="text-xs text-gray-500">Active Channels</div>
        </div>
      </div>

      {/* Visualization Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* 3D Journey Graph */}
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>📊</span> Journey State Machine
              <span className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded-full">3D Interactive</span>
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              Each node is a <span className="text-white">Markov state</span>. Drag to rotate.
              Connections show transition probabilities between touchpoints.
            </p>
          </div>
          <div style={{ height: '400px' }}>
            <Journey3D />
          </div>
          <div className="p-3 bg-gray-900/50 text-xs text-gray-500 border-t border-gray-800">
            💡 <strong>Reading this:</strong> START → channel states → CONVERSION. The path shows how users flow through your funnel.
          </div>
        </div>

        {/* Radial Tree */}
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>🌳</span> Channel Hierarchy
              <span className="text-xs bg-purple-900/50 text-purple-400 px-2 py-0.5 rounded-full">Animated</span>
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              <span className="text-white">Center:</span> All journeys → <span className="text-white">Inner ring:</span> Channels → <span className="text-white">Outer ring:</span> Individual journeys
            </p>
          </div>
          <div className="p-2">
            <div className="flex gap-2 mb-2">
              <button id="tree-rotate" className="px-3 py-1.5 bg-gray-800 border border-purple-500/50 rounded text-xs hover:bg-purple-900/30 transition-all">
                Auto-Rotate: On
              </button>
              <div className="flex items-center gap-3 text-xs text-gray-500 ml-auto">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Search</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Direct</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Email</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span> Paid</span>
              </div>
            </div>
            <div id="radial-tree-container" className="rounded-lg" style={{ height: '380px', background: 'rgba(10, 10, 15, 1)' }}>
              <canvas id="radial-tree-canvas" style={{ width: '100%', height: '100%' }}></canvas>
            </div>
          </div>
          <div className="p-3 bg-gray-900/50 text-xs text-gray-500 border-t border-gray-800">
            💡 <strong>Hover</strong> over nodes to see attributed values. Node size reflects touchpoint frequency.
          </div>
        </div>

        {/* Parallel Coordinates */}
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>📈</span> Multi-Dimensional Journey View
              <span className="text-xs bg-green-900/50 text-green-400 px-2 py-0.5 rounded-full">Parallel Coordinates</span>
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              Each line = one touchpoint. See how journeys traverse: Channel → Position → Touchpoints → Duration → Value → Conversion
            </p>
          </div>
          <div className="p-2">
            <div className="flex gap-3 mb-2 items-center">
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-400">Filter:</label>
                <select id="cluster-filter" className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs">
                  <option value="all">All Channels</option>
                  <option value="Search">Search</option>
                  <option value="Social">Social</option>
                  <option value="Email">Email</option>
                  <option value="Direct">Direct</option>
                  <option value="Paid">Paid</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-400">Opacity:</label>
                <input id="line-opacity" type="range" min="0.2" max="1" step="0.1" defaultValue="0.5" className="w-20 accent-amber-500" />
              </div>
            </div>
            <div id="parallel-container" className="rounded-lg" style={{ height: '340px', background: 'rgba(10, 10, 15, 1)' }}>
              <canvas id="parallel-canvas" style={{ width: '100%', height: '100%' }}></canvas>
            </div>
          </div>
          <div className="p-3 bg-gray-900/50 text-xs text-gray-500 border-t border-gray-800">
            💡 <strong>Reading this:</strong> Lines going to &quot;Converted: Yes&quot; (top right) show successful paths. Hover to highlight entire journey.
          </div>
        </div>

        {/* State Flow */}
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>🌊</span> Transition Flow River
              <span className="text-xs bg-amber-900/50 text-amber-400 px-2 py-0.5 rounded-full">Live Animation</span>
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              Animated particles show <span className="text-white">transition probability flow</span>. Wider streams = more frequent transitions.
            </p>
          </div>
          <div id="alpha-sweep" className="rounded-lg m-2" style={{ height: '380px', background: 'rgba(10, 10, 15, 1)' }}>
            <canvas id="flow-canvas" style={{ width: '100%', height: '100%' }}></canvas>
          </div>
          <div className="p-3 bg-gray-900/50 text-xs text-gray-500 border-t border-gray-800">
            💡 <strong>This is your Markov matrix visualized.</strong> Each particle represents probability mass flowing between states.
          </div>
        </div>
      </div>

      {/* Attribution Summary Table */}
      <div className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden mb-8">
        <div className="p-4 border-b border-gray-800 bg-gray-900/50">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <span>📋</span> Attribution Results
            <span className="text-xs bg-gray-700 px-2 py-0.5 rounded-full text-gray-400">α = {alphaVal.toFixed(1)}</span>
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Final credit allocation with <span className="text-amber-400">95% confidence intervals</span> from Bootstrap + Dirichlet UQ
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-800/50 text-left">
                <th className="p-3 text-gray-400 font-medium">Channel</th>
                <th className="p-3 text-gray-400 font-medium">Hybrid Share</th>
                <th className="p-3 text-gray-400 font-medium">Attributed Value</th>
                <th className="p-3 text-gray-400 font-medium">95% CI</th>
                <th className="p-3 text-gray-400 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody id="stats-table-body" className="divide-y divide-gray-800"></tbody>
          </table>
        </div>
        <div className="p-3 bg-gray-900/50 text-xs text-gray-500 border-t border-gray-800">
          💡 <strong>CI = Confidence Interval.</strong> Narrower range = more certainty. &quot;High&quot; confidence means the interval is &lt;10% of the value.
        </div>
      </div>

      {/* Model Configuration & Philosophy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>⚙️</span> Model Configuration
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div><span className="text-gray-500">IR Version:</span> <span className="text-white">1.0.0</span></div>
              <div><span className="text-gray-500">Markov Order:</span> <span className="text-white">First-order</span></div>
              <div><span className="text-gray-500">Shapley Mode:</span> <span className="text-white">Exact enumeration</span></div>
            </div>
            <div className="space-y-2">
              <div><span className="text-gray-500">Coalitions:</span> <span className="text-white">2^n = 32</span></div>
              <div><span className="text-gray-500">UQ Method:</span> <span className="text-white">Bootstrap + Dirichlet</span></div>
              <div><span className="text-gray-500">Psychographic:</span> <span className="text-amber-400">Context-weighted</span></div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-800 text-xs text-gray-500">
            <strong className="text-white">Key Invariant:</strong> All channel shares sum to exactly 1.0 (Efficiency Axiom enforced)
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-900/20 to-gray-900/30 border border-purple-800/30 rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>🛡️</span> Ethical Boundary
          </h2>
          <p className="text-sm text-gray-400 mb-4">
            This is a <span className="text-purple-400 font-medium">Personal Epistemic Instrument</span>—designed for
            reflection, not surveillance. It helps you understand your own behavioral patterns.
          </p>
          <div className="bg-gray-900/50 rounded-lg p-3 text-xs">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-green-400">✓</span>
              <span className="text-gray-400"><strong className="text-white">Allowed:</strong> Aggregate behavior, transition patterns, declared context</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-red-400">✗</span>
              <span className="text-gray-400"><strong className="text-white">Prohibited:</strong> Mental state inference, predictive profiling, surveillance</span>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-3 italic">
            &quot;Layer 4 (Psychographic Inference) is architecturally prohibited. We analyze what you did, never what you felt.&quot;
          </p>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mt-8 bg-gray-900/30 border border-gray-800 rounded-xl p-5">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span>❓</span> Common Questions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h3 className="text-white font-medium mb-1">Why not just use last-click attribution?</h3>
            <p className="text-xs text-gray-500">Last-click ignores all earlier touchpoints. A user might see 5 ads before converting—last-click gives 100% credit to the final one. Our hybrid model credits the entire journey fairly.</p>
          </div>
          <div>
            <h3 className="text-white font-medium mb-1">What makes this &quot;first principles&quot;?</h3>
            <p className="text-xs text-gray-500">Every calculation is derivable from axioms. Shapley values satisfy Efficiency, Symmetry, Dummy, and Additivity. Markov chains are provably row-stochastic. No black boxes.</p>
          </div>
          <div>
            <h3 className="text-white font-medium mb-1">What do the confidence intervals mean?</h3>
            <p className="text-xs text-gray-500">We resample your data 10,000 times (Bootstrap) and add Bayesian smoothing (Dirichlet). The 95% CI shows the range where the true value likely falls.</p>
          </div>
          <div>
            <h3 className="text-white font-medium mb-1">Can I trust these numbers for decisions?</h3>
            <p className="text-xs text-gray-500">Yes, within the model&apos;s assumptions. Check the CI width—narrow = high confidence. Compare against holdout tests. This is a scientific instrument, not an oracle.</p>
          </div>
        </div>
      </div>
    </div>
  );
}