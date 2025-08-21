import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

// Animated floating particles/bubbles
function AnimatedParticles({ count = 1000 }) {
  const points = useRef();
  const particlesPosition = useMemo(() => {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return positions;
  }, [count]);

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.x = state.clock.elapsedTime * 0.1;
      points.current.rotation.y = state.clock.elapsedTime * 0.15;
      
      // Animate individual particles
      const positions = points.current.geometry.attributes.position.array;
      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        positions[i3 + 1] += Math.sin(state.clock.elapsedTime + i * 0.01) * 0.002;
      }
      points.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={points} positions={particlesPosition} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#60a5fa"
        size={0.02}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.6}
      />
    </Points>
  );
}

// Floating geometric shapes
function FloatingShapes() {
  const groupRef = useRef();
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = state.clock.elapsedTime * 0.05;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.08;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Floating spheres */}
      {Array.from({ length: 8 }, (_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        const radius = 6;
        return (
          <FloatingSphere
            key={i}
            position={[
              Math.cos(angle) * radius,
              Math.sin(angle * 2) * 2,
              Math.sin(angle) * radius
            ]}
            color={i % 2 === 0 ? "#3b82f6" : "#6366f1"}
            delay={i * 0.5}
          />
        );
      })}
      
      {/* Floating boxes */}
      {Array.from({ length: 6 }, (_, i) => {
        const angle = (i / 6) * Math.PI * 2;
        const radius = 8;
        return (
          <FloatingBox
            key={i}
            position={[
              Math.cos(angle + Math.PI) * radius,
              Math.sin(angle * 1.5) * 3,
              Math.sin(angle + Math.PI) * radius
            ]}
            color="#0ea5e9"
            delay={i * 0.7}
          />
        );
      })}
    </group>
  );
}

function FloatingSphere({ position, color, delay }) {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + delay) * 0.5;
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.3;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.2;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.1, 16, 16]} />
      <meshBasicMaterial color={color} transparent opacity={0.7} />
    </mesh>
  );
}

function FloatingBox({ position, color, delay }) {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.cos(state.clock.elapsedTime + delay) * 0.3;
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2;
      meshRef.current.rotation.z = state.clock.elapsedTime * 0.1;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.15, 0.15, 0.15]} />
      <meshBasicMaterial color={color} transparent opacity={0.6} />
    </mesh>
  );
}

// Main background component
export default function ThreeBackground() {
  return (
    <div className="fixed inset-0 -z-10">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <AnimatedParticles count={800} />
        <FloatingShapes />
      </Canvas>
    </div>
  );
}