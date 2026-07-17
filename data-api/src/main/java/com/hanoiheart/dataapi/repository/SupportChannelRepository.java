package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.SupportChannel;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SupportChannelRepository extends JpaRepository<SupportChannel, Long> {
    List<SupportChannel> findByIsActiveTrueOrderBySortOrderAscIdAsc();
}
